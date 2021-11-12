#!/usr/bin/env python3
import argparse
import os
import sys

fakepulsarperiod = 10  # seconds


def _main():
    args = get_args()
    validate_args(args)

    timediffsec = args.timediff / 1000.0

    cand = parse_snoopy(args.snoopylog)
    pulsewidthms = float(cand[3]) * 1.7  # filterbank width = 1.7ms
    dm = float(cand[5])
    mjd = float(cand[7])

    # Figure out the time at the midpoint of the pulse
    midmjd = (
        mjd
        - (
            dm * 0.00415 / ((args.freq / 1e3) ** 2)
            - dm * 0.00415 / ((args.freq + 168) / 1e3) ** 2
        )
        / 86400.0
    )

    # Figure out the best int time
    bestinttime = calc_best_int_time(args.corrstartmjd, midmjd)
    print(bestinttime)

    polycorefmjd, hh, mm, ss = calc_polyco_ref_mjd(args.corrstartmjd)

    # Write out the polyco file
    write_polyco(polycorefmjd, hh, mm, ss)

    # Now write out a binconfig for the gate
    write_gate(mjd, pulsewidthms)

    # Make an RFI binconfig
    rfistartphase1 = (
        gatestartphase - 0.02 / fakepulsarperiod
    )  # RFI gate (early side) starts 20ms before the start of the pulse
    rfiendphase1 = (
        gatestartphase - 0.004 / fakepulsarperiod
    )  # RFI gate (early side) ends 4ms before the start of the pulse
    rfistartphase2 = (
        gateendphase + 0.004 / fakepulsarperiod
    )  # RFI gate (late side) starts 4ms after the end of the pulse
    rfiendphase2 = (
        gateendphase + 0.02 / fakepulsarperiod
    )  # RFI gate (early side) ends 20ms after the end of the pulse

    with open("craftfrb.rfi.binconfig", "w") as binconfout:
        binconfout.write("NUM POLYCO FILES:   1\n")
        binconfout.write(
            "POLYCO FILE 0:      %s/craftfrb.polyco\n" % os.getcwd()
        )
        binconfout.write("NUM PULSAR BINS:    4\n")
        binconfout.write("SCRUNCH OUTPUT:     TRUE\n")
        binconfout.write("BIN PHASE END 0:    %.9f\n" % rfistartphase1)
        binconfout.write("BIN WEIGHT 0:       0.0\n")
        binconfout.write("BIN PHASE END 1:    %.9f\n" % rfiendphase1)
        binconfout.write("BIN WEIGHT 1:       1.0\n")
        binconfout.write("BIN PHASE END 2:    %.9f\n" % rfistartphase2)
        binconfout.write("BIN WEIGHT 2:       0.0\n")
        binconfout.write("BIN PHASE END 3:    %.9f\n" % rfiendphase2)
        binconfout.write("BIN WEIGHT 3:       1.0\n")
        binconfout.close()

    # And make a high time resolution binconfig (216 microsec x bin width + 2ms either side)
    binstartmjd = mjd - fakepulsarperiod * pulsewidthms / (
        2 * 86400000.0
    )  # pulse width is in ms at this point
    gateendmjd = (
        gatestartmjd + pulsewidthms / 86400000.0
    )  # pulse width is in ms at this point
    binmicrosec = 216
    extrawidth = 2  # ms on either side of the snoopy detected pulse
    binstartphase = gatestartphase - float(extrawidth) / (
        1000.0 * fakepulsarperiod
    )
    bindeltaphase = binmicrosec / (fakepulsarperiod * 1e6)
    numbins = int((pulsewidthms + 2 * extrawidth) / (binmicrosec / 1000.0))
    with open("craftfrb.bin.binconfig", "w") as binconfout:
        binconfout.write("NUM POLYCO FILES:   1\n")
        binconfout.write(
            "POLYCO FILE 0:      %s/craftfrb.polyco\n" % os.getcwd()
        )
        binconfout.write("NUM PULSAR BINS:    %d\n" % (numbins + 1))
        binconfout.write("SCRUNCH OUTPUT:     FALSE\n")
        for i in range(numbins + 1):
            phasestr = ("BIN PHASE END %d:" % i).ljust(20)
            weightstr = ("BIN WEIGHT %d:" % i).ljust(20)
            binconfout.write(
                f"{phasestr}{binstartphase + i*bindeltaphase:.9f}\n"
            )
            binconfout.write("%s1.0\n" % (weightstr))
        binconfout.close()
    binscale = bindeltaphase / (
        rfiendphase2 + rfiendphase1 - rfistartphase2 - rfistartphase1
    )

    # And also make a "finders" binconfig, with just 5 bins spanning from the end of RFI window 1
    # through to the start of RFI window 2 (which will then normally be 2-3 ms wide each
    numfinderbins = 19
    # bindeltaphase = (rfistartphase2 - rfiendphase1)/numfinderbins
    # TEMP: force 100 ms bins to get 2.5s of data
    binstartphase = gatestartphase
    bindeltaphase = 0.01
    with open("craftfrb.finder.binconfig", "w") as binconfout:
        binconfout.write("NUM POLYCO FILES:   1\n")
        binconfout.write(
            "POLYCO FILE 0:      %s/craftfrb.polyco\n" % os.getcwd()
        )
        binconfout.write("NUM PULSAR BINS:    %d\n" % (numfinderbins + 1))
        binconfout.write("SCRUNCH OUTPUT:     FALSE\n")
        for i in range(numfinderbins + 1):
            phasestr = ("BIN PHASE END %d:" % i).ljust(20)
            weightstr = ("BIN WEIGHT %d:" % i).ljust(20)
            binconfout.write(
                f"{phasestr}{binstartphase + i*bindeltaphase:.9f}\n"
            )
            binconfout.write("%s1.0\n" % (weightstr))
        binconfout.close()
    finderbinscale = bindeltaphase / (
        rfiendphase2 + rfiendphase1 - rfistartphase2 - rfistartphase1
    )

    # And write out a little script ready to do the various subtractions
    gatescale = (gateendphase - gatestartphase) / (
        rfiendphase2 + rfiendphase1 - rfistartphase2 - rfistartphase1
    )
    with open("dosubtractions.sh", "w") as subout:
        subout.write(
            "uvsubScaled.py FRB_GATE.FITS FRB_RFI.FITS %.9f\n" % (gatescale)
        )
        for i in range(numbins):
            subout.write(
                "uvsubScaled.py FRB_BIN%02d.FITS FRB_RFI.FITS %.9f\n"
                % (i, binscale)
            )
        for i in range(numfinderbins):
            subout.write(
                "uvsubScaled.py FRB_FINDERBIN%02d.FITS FRB_RFI.FITS %.9f\n"
                % (i, finderbinscale)
            )
        subout.close()


def get_args() -> argparse.Namespace:
    """Parse command line arguments

    :return: Command line argument paramters
    :rtype: :class:`argparse.Namespace`
    """
    parser = argparse.ArgumentParser(
        description="Turn a snoopy log into a binconfig and polyco for DiFX."
    )
    parser.add_argument("snoopylog", metavar="S", help="The snoopy log file")
    parser.add_argument(
        "-f",
        "--freq",
        type=float,
        default=-1,
        help="The reference freq at which snoopy DM was calculated",
    )
    parser.add_argument(
        "--timediff",
        type=float,
        default=-99999,
        help="The time difference between the VCRAFT and snoopy log arrival "
        "times for the pulse, including geometric delay, in ms",
    )
    parser.add_argument(
        "--corrstartmjd",
        type=float,
        default=-1,
        help="When the correlation will start",
    )
    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> None:
    """Validate arguments

    :param args: Command line arguments
    :type args: :class:`argparse.Namespace`
    """
    if args.freq < 0:
        print(
            "You have to supply a frequency for the snoopy files! Don't be "
            "lazy, that's how accidents happen."
        )
        sys.exit()

    if args.timediff < -10000:
        print(
            "You have to specify a timediff! It should just be the geometric "
            "delay from ASKAP to the geocentre, "
        )
        print(
            "now everything has been fixed.  Don't be lazy, that's how "
            "accidents happen."
        )
        sys.exit()

    if args.corrstartmjd < 0:
        print(
            "You have to specify a corrstartmjd. getGeometricDelay.py will "
            "give it to you"
        )
        sys.exit()


def parse_snoopy(snoopy_file: str) -> "list[str]":
    """Parse snoopy file, returning a candidate as a list of strings.

    We expect this file to only contain one candidate (the triggering
    candidate), so we only return one line.

    :param snoopy_file: Path to snoopy candidate file
    :type snoopy_file: str
    :return: Candidate information as a list of strings. Each string is
        a whitespace-separated value in the candidate file.
    :rtype: list[str]
    """
    nocommentlines = []
    for line in open(snoopy_file):
        print(line)
        if len(line) > 1 and not line[0] == "#":
            nocommentlines.append(line)
            print(f"Snoopy info {nocommentlines}")
    if len(nocommentlines) != 1:
        print("ERROR: No information found")
        sys.exit()

    return nocommentlines[0].split()


def calc_best_int_time(corrstartmjd: float, midmjd: float) -> float:
    """Calculate the best integration time such that the FRB should be
    within a single integration

    :param corrstartmjd: Start time of correlation (in MJD)
    :type corrstartmjd: float
    :param midmjd: Central time of the FRB (in MJD)
    :type midmjd: float
    :return: Best integration time (in seconds)
    :rtype: float
    """
    subintsec = 0.13824
    bestinttime = 2 * (midmjd - corrstartmjd) * 86400
    nsubints = int(round(bestinttime / subintsec))
    bestinttime = nsubints * subintsec
    return bestinttime


def calc_polyco_ref_mjd(corrstartmjd: float) -> "tuple[float, int, int, int]":
    """Calculate the start time for the polyco by going back to the
    integer second boundary immediately before the correlation start
    time.

    :param corrstartmjd: Start time of correlation (in MJD)
    :type corrstartmjd: float
    :return: Polyco reference time (in MJD) and the hour, minute, and
        seconds of that time as integers
    :rtype: tuple[float, int, int, int]
    """
    polycorefmjdint = int(args.corrstartmjd)
    polycorefseconds = int(
        (args.corrstartmjd - int(args.corrstartmjd)) * 86400
    )

    hh = polycorefseconds // 3600
    mm = (polycorefseconds - hh * 3600) // 60
    ss = polycorefseconds - (hh * 3600 + mm * 60)

    polycorefmjd = polycorefmjdint + float(polycorefseconds) / 86400.0

    return polycorefmjd, hh, mm, ss


def write_polyco(
    polycorefmjd: float,
    hh: int,
    mm: int,
    ss: int,
    dm: float
) -> None:
    """Write out the polyco file

    :param polycorefmjd: Polyco reference time (in MJD)
    :type polycorefmjd: float
    :param hh: Hour of the reference time
    :type hh: int
    :param mm: Minute of the reference time
    :type mm: int
    :param ss: Second of the reference time
    :type ss: int
    :param dm: Dispersion measure of the triggering FRB candidate
    :type dm: float
    """
    with open("craftfrb.polyco", "w") as polycoout:
        polycoout.write(
            f"fake+fake DD-MMM-YY %02d%02d%05.2f %.15f %.4f 0.0 0.0\n"
            % (hh, mm, ss, polycorefmjd, dm)
        )
        polycoout.write(
            f"0.0 {1.0/float(fakepulsarperiod):.3f} 0 100 3 {args.freq:.3f}\n"
        )
        polycoout.write(
            "0.00000000000000000E-99 "
            "0.00000000000000000E-99 "
            "0.00000000000000000E-99\n"
        )
        polycoout.close()


def write_gate(
    cand: "list[str]", 
    timediff: float, 
    polycorefmjd: float,
) -> None:
    """Write the gate binconfig file.

    The gate mode has two bins: 
        > On-pulse (from 0.5 seconds before to 1.5 seconds after the
          burst)
        > Off-pulse (everything else)
    
    :param cand: Fields of the snoopy candidate
    :type cand: list[str]
    :param timediff: The time difference between the VCRAFT and snoopy 
        log arrival times for the pulse, including geometric delay, in 
        ms
    :type timediff: float
    :param polycorefmjd: Polyco reference time in MJD
    :type polycorefmjd: float
    """
    gatestartmjd = mjd - (pulsewidthms + 1000) / (
        2 * 86400000.0
    )  # pulse width is in ms at this point
    gateendmjd = (
        gatestartmjd + (pulsewidthms + 2000) / 86400000.0
    )  # pulse width is in ms at this point
    gatestartphase = (
        86400.0 * (gatestartmjd - polycorefmjd) + timediffsec
    ) / fakepulsarperiod
    gateendphase = (
        86400.0 * (gateendmjd - polycorefmjd) + timediffsec
    ) / fakepulsarperiod

    with open("craftfrb.gate.binconfig", "w") as binconfout:
        binconfout.write("NUM POLYCO FILES:   1\n")
        binconfout.write(
            "POLYCO FILE 0:      %s/craftfrb.polyco\n" % os.getcwd()
        )
        binconfout.write("NUM PULSAR BINS:    2\n")
        binconfout.write("SCRUNCH OUTPUT:     TRUE\n")
        binconfout.write("BIN PHASE END 0:    %.9f\n" % gatestartphase)
        binconfout.write("BIN WEIGHT 0:       0.0\n")
        binconfout.write("BIN PHASE END 1:    %.9f\n" % gateendphase)
        binconfout.write("BIN WEIGHT 1:       1.0\n")
        binconfout.close()


if __name__ == "__main__":
    _main()
