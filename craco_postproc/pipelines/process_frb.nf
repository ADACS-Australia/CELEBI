nextflow.enable.dsl=2

include { create_empty_file } from './utils'
include { correlate as corr_finder; correlate as corr_rfi;
    correlate as corr_field; subtract_rfi } from './correlate'
include { apply_flux_cal_solns_finder as cal_finder;
    apply_flux_cal_solns_field as cal_field; get_peak } from './calibration'
include { apply_offset; generate_binconfig } from './localise'
include { beamform as bform_frb } from './beamform'

params.fieldimage = ""
params.flagfinder = ""
params.skiprfi = false

beamform_dir = "$baseDir/../beamform/"

process plot {
    /*
        Plot dynamic spectra across different time resolutions to produce
        summary plot.

        Input
            label: val
                FRB name and context of process instance as a string (no
                spaces)
            fnames_file: path
                File containing file names of dynamic spectra
            dynspecs: path
                Stokes parameter dynamic spectra
            centre_freq: val
                Central frequency of fine spectrum (MHz)
            dm: val
                Dispersion measure the data has been dedispersed to
            xy: path
                High-time resolution time series of X and Y pols
        
        Output:
            plot: path
                Plotted dynamic spectra across different time resolutions
            crops: path
                Directory containing cropped numpy files
    */
    publishDir "${params.publish_dir}/${params.label}/htr", mode: "copy"

    input:
        val label
        path fnames_file
        path dynspecs
        val centre_freq
        val dm
        path xy
    
    output:
        path "*.png"
        path "crops", emit: crops
    
    script:
        """
        if [ "$params.ozstar" == "true" ]; then
            module load gcc/9.2.0
            module load openmpi/4.0.2
            module load python/3.7.4
            module load numpy/1.18.2-python-3.7.4
            module load matplotlib/3.2.1-python-3.7.4
        fi
        args="-s $fnames_file"
        args="\$args -f $centre_freq"
        args="\$args -l $label"
        args="\$args -d $dm"
        args="\$args -x ${label}*X_t*npy"
        args="\$args -y ${label}*Y_t*npy"

        mkdir crops

        python3 $beamform_dir/plot.py \$args
        """
    
    stub:
        """
        touch stub.png
        mkdir crops
        """
}

process npy2fil {
    /*
        Convert cropped numpy files to filterbank

        Input
            label: val
                FRB name and context of process instance as a string (no
                spaces)
            crops: path
                Directory containing cropped numpy files to convert
            startmjd: val
                Earliest data start time in Modified Julian Day (MJD) 
            centre_freq: val
                Central frequency of fine spectrum (MHz)
            final_position: path
                Text file containing final position and error
            
        Output:
            fils: path
                Directory containing converted filterbank files
    */
    publishDir "${params.publish_dir}/${params.label}/htr/fils", mode: "copy"

    input:
        val label
        path crops
        val startmjd
        val centre_freq
        path final_position
    
    output:
        path "*fil"
    
    script:
        """
        if [ "$params.ozstar" == "true" ]; then
            . $launchDir/../setup_proc
        fi

        # invoke script to avoid clashes between Nextflow's parsing and bash's
        $beamform_dir/do_npy2fil.sh $final_position $params.label $startmjd \
                                    $centre_freq $beamform_dir
        """

    stub:
        """
        touch stub.fil
        """
}

workflow process_frb {
    /*
        Process voltages to obtain an FRB position

        Take
            flux_cal_solns: path
                Flux calibrator solutions tarball
            pol_cal_solns: path
                Polarisation calibration solutions in a text file
    */
    take:
        flux_cal_solns
        pol_cal_solns

    main:
        binconfig = generate_binconfig()
        // Correlate finder
        finder_fits_path = "${params.publish_dir}/${params.label}/loadfits/finder/finderbin20.fits"
        if(new File(finder_fits_path).exists()) {
            finder_fits = Channel.fromPath(
                "${params.publish_dir}/${params.label}/loadfits/finder/finderbin*.fits"
            )
        }
        else {
            finder_fits = corr_finder(
                "finder", params.data_frb, params.ra_frb, params.dec_frb, 
                binconfig.finder, binconfig.polyco, binconfig.int_time, "finder"
            )
        }

        // Correlate RFI (if not directly flagging finder)
        rfi_fits_path = "${params.publish_dir}/${params.label}/loadfits/rfi/${params.label}_rfi.fits"
        if ( new File(rfi_fits_path).exists() ) {
            rfi_fits = Channel.fromPath(rfi_fits_path)
        }
        else {
            if(!params.skiprfi) {
                rfi_fits = corr_rfi(
                    "${params.label}_rfi", params.data_frb, params.ra_frb, 
                    params.dec_frb, binconfig.rfi, binconfig.polyco, binconfig.int_time, "rfi"
                )
            }
        }

        // Correlate field (if not using deep field image)
        field_fits_path = "${params.publish_dir}/${params.label}/loadfits/field/${params.label}_field.fits"
        if((params.fieldimage != "") or new File(field_fits_path).exists() ) {
            if(params.fieldimage == "") {
                field_fits = Channel.fromPath(field_fits_path)
            }
            else {
                field_fits = Channel.fromPath("${params.fieldimage}")
            }
        }
        else {
            empty_file = create_empty_file("file")
            field_fits = corr_field(
                "${params.label}_field", params.data_frb, params.ra_frb, 
                params.dec_frb, empty_file, empty_file, 0, "field"
            )
        }

        // Calibrate (i.e. image finder and field)
        frb_jmfit_path = "${params.publish_dir}/${params.label}/finder/${params.label}.jmfit"
        frb_pos_path = "${params.publish_dir}/${params.label}/position/${params.label}_final_position.txt"
        if(new File(frb_jmfit_path).exists() && new File(frb_pos_path).exists()) {
            askap_frb_pos = Channel.fromPath(frb_jmfit_path)
            final_position = Channel.fromPath(frb_pos_path)
        }
        else if(params.calibrate) {
            if((params.fieldimage == "") && (params.fieldflagfile == "")){
                println "No field flag file!"
                System.exit(1)
            }
            
            if(params.skiprfi){
                no_rfi_finder_fits = finder_fits
            }
            else {
                no_rfi_finder_fits = subtract_rfi(
                    finder_fits, rfi_fits, binconfig.subtractions
                )                
            }

            bins_out = cal_finder(
                no_rfi_finder_fits, flux_cal_solns
            )
            bin_jmfits = bins_out.jmfit
            bin_fits_images = bins_out.fits_image
            bin_regs = bins_out.reg
            bin_mss = bins_out.ms

            askap_frb_pos = get_peak(
                bin_jmfits.collect(), bin_fits_images.collect(), 
                bin_regs.collect(), bin_mss.collect()
            ).peak_jmfit

            field_sources = cal_field(
                field_fits, flux_cal_solns, params.fieldflagfile, askap_frb_pos
            ).jmfit

            final_position = apply_offset(field_sources, askap_frb_pos).final_position
        }

        if(params.beamform) {
            bform_frb(
                params.label, params.data_frb, askap_frb_pos, flux_cal_solns, 
                pol_cal_solns, params.dm_frb, params.centre_freq_frb, "-ds -t -XYIQUV"
            )
            plot(
                params.label, bform_frb.out.dynspec_fnames, bform_frb.out.htr_data,
                params.centre_freq_frb, params.dm_frb, bform_frb.out.xy
            )
            npy2fil(params.label, plot.out.crops, 0, params.centre_freq_frb, final_position)
        }
}
