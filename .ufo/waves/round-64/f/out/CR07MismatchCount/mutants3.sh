set -u
D=/fast/scratch/hyaku/kama-r64/f/CR07MismatchCount/clone
S=/fast/scratch/hyaku/kama-r64/f/CR07MismatchCount
TIP=23b3fdb1a925129a9961cf551f6d40bf251602cb
run_mut () {
  name=$1
  cd $D; git reset -q --hard $TIP
  python3 $S/mut_$name.py $D
  git -C $D add -A
  git -C $D -c user.name=seat -c user.email=seat@seat.invalid commit -q -m "mutant $name"
  T=$(git -C $D rev-parse HEAD)
  mkdir -p $S/work-$name
  (cd $D/tools && python3 round64-c2-counter.py --repo $D --tip $T --work $S/work-$name) > $S/mut-$name.out 2> $S/mut-$name.err
  echo "EXIT=$? $name $T" >> $S/mut-$name.out
  echo "--- $name:"; cat $S/mut-$name.out
}
run_mut m10_verdictword
run_mut m11_posrunfact
run_mut m8_delcounter
run_mut m9_delshenon
