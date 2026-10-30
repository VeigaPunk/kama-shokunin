set -u
D=/fast/scratch/hyaku/kama-r64/f/CR07MismatchCount/clone
S=/fast/scratch/hyaku/kama-r64/f/CR07MismatchCount
TIP=23b3fdb1a925129a9961cf551f6d40bf251602cb
cd $D; git reset -q --hard $TIP
python3 $S/mut_m13_printer.py $D
git -C $D add -A
git -C $D -c user.name=seat -c user.email=seat@seat.invalid commit -q -m "mutant m13"
T=$(git -C $D rev-parse HEAD)
mkdir -p $S/work-m13
(cd $D/tools && python3 round64-c2-counter.py --repo $D --tip $T --work $S/work-m13) > $S/mut-m13_printer.out 2> $S/mut-m13_printer.err
echo "EXIT=$? m13 $T" >> $S/mut-m13_printer.out
cat $S/mut-m13_printer.out
