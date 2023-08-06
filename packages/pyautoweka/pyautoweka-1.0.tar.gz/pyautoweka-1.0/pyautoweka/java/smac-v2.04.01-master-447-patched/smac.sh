#!/usr/bin/env bash
SMAC_MEMORY_INPUT=$SMAC_MEMORY
SMACMEM=1024
test "$SMAC_MEMORY_INPUT" -ge 1 2>&- && SMACMEM=$SMAC_MEMORY_INPUT
EXEC=ca.ubc.cs.beta.smac.executors.AutomaticConfigurator
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "Starting with $SMACMEM MB of RAM"
exec java -Xmx"$SMACMEM"m -cp "$DIR/patches:$DIR/smac.jar:$DIR/commons-math-2.2.jar:$DIR/Jama-1.0.2.jar:$DIR/commons-math3-3.0.jar:$DIR/conf/:$DIR/numerics4j-1.3.jar:$DIR/slf4j-api-1.6.4.jar:$DIR/commons-collections-3.2.1.jar:$DIR/commons-io-2.1.jar:$DIR/fastrf.jar:$DIR/jcommander.jar:$DIR/opencsv-2.3.jar:$DIR/aclib.jar:$DIR/truezip-samples-7.4.3-jar-with-dependencies.jar:$DIR/logback-access-1.0.0.jar:$DIR/logback-core-1.0.0.jar:$DIR/logback-classic-1.0.0.jar:$DIR/patches" $EXEC "$@"

