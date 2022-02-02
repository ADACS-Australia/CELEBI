nextflow.enable.dsl=2

include { create_empty_file } from './utils'
include { correlate } from './correlate'
include { apply_flux_cal_solns } from './calibration'
include { localise; apply_offset } from './localise'
include { beamform } from './beamform'

process generate_binconfig {
    input:
        val data
        path snoopy

    output:
        path "craftfrb.gate.binconfig", emit: gate
        path "craftfrb.rfi.binconfig", emit: rfi
        path "craftfrb.polyco", emit: polyco
        env int_time, emit: int_time

    script:
        """
        tmp_file=".TMP_\$BASHPID"
        $baseDir/craftpy2/getGeocentricDelay.py $data_frb $snoopy > \$tmp_file

        sl2f_cmd=`tail -1 \$tmp_file`
        sl2f_cmd="$baseDir/craftpy2/\$sl2f_cmd"
        \$sl2f_cmd > sl2f.out
        int_time=`cat sl2f.out`
        """
}

workflow process_frb {
    take:
        label   // val
        data    // val
        snoopy  // path
        fcm // val
        ra0 // val
        dec0    // val
        flux_cal_solns  // path
        pol_cal_solns // path
        cpasspoly   // val
        num_ints    // val
        int_len // val
        offset  // val
        dm  // val
        centre_freq // val

    main:
        binconfigs = generate_binconfig(data, snoopy)

        gate_fits = correlate(
            "${label}_gate", data, fcm, ra0, dec0, binconfigs.gate, binconfigs.int_time
        )
        rfi_fits = correlate(
            "${label}_rfi", data, fcm, ra0, dec0, binconfigs.rfi, binconfigs.int_time
        )
        empty_file = create_empty_file("file")
        field_fits = correlate(
            "${label}_field", data, fcm, ra0, dec0, empty_file, 0
        )

        no_rfi_gate_fits = subtract_rfi(gate_fits, rfi_fits)
        no_rfi_field_fits = subtract_rfi(field_fits, rfi_fits)

        gate_image = apply_flux_cal_solns(
            no_rfi_gate_fits, flux_cal_solns, empty_file, label, cpasspoly
        )
        field_image = apply_flux_cal_solns(
            no_rfi_field_fits, flux_cal_solns, empty_file, label, cpasspoly
        )

        askap_frb_pos = localise(gate_image)
        apply_offset(field_image, askap_frb_pos)

        beamform(
            label, data, fcm, askap_frb_pos, flux_cal_solns, pol_cal_solns,
            num_ints, int_len, offset, dm, centre_freq
        )

    emit:
        true_pos = apply_offset.out
        frb_htr_data = beamform.out
}
