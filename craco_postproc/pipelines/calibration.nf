process determine_flux_cal_solns {
    input:
        path cal_fits
        val flagfile
        val target
        val cpasspoly

    output:
        path "calibration_noxpol_${target}.tar.gz"

    script:
        """
        if [ "$flagfile" == "" ]; then
            echo "You now need to write the flagfile for ${cal_fits} and provide it with --fluxflagfile!"
            exit 2
        fi        

        args="--calibrateonly"
        args="\$args -c $cal_fits"
        args="\$args --uvsrt"
        args="\$args -u 51"
        args="\$args --src=$target"
        args="\$args --cpasspoly=$cpasspoly"
        args="\$args -f 15"
        args="\$args --flagfile=$flagfile"

        calibrateFRB.py \$args
        """
}

process apply_flux_cal_solns {
    input:
        path target_fits
        path cal_solns
        val flagfile
        val target
        val cpasspoly
        val dummy   // so we can force only one instance to go at a time

    output:
        path "*.image"

    script:
        """
        if [ "$flagfile" == "" ]; then
            echo "You now need to write the flagfile for ${target_fits} and provide it with --polflagfile!"
            exit 2
        fi    
        tar -xzvf $cal_solns

        args="--targetonly"
        args="\$args -t $target_fits"
        args="\$args -r 3"
        args="\$args --cpasspoly=$cpasspoly"
        args="\$args -i"
        args="\$args --dirtymfs"
        args="\$args -a 16"
        args="\$args -u 500"
        args="\$args --skipplot"
        args="\$args --src=$target"

        if [ `wc -c $flagfile | awk '{print \$1}'` != 0 ]; then
            args="\$args --tarflagfile=$flagfile"
        fi

        calibrateFRB.py \$args
        """    
}

process determine_pol_cal_solns {
    input:
        path htr_data

    output:
        path "polcal.dat"
    
    script:
        """
        touch polcal.dat
        """
}
