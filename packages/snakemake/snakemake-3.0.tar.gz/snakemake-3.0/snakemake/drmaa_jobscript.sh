#!/bin/sh
{workflow.snakemakepath} --snakefile {workflow.snakefile} \
--force -j{cores} --keep-target-files --input-wait {input_wait} \
--directory {workdir} --nocolor --notemp --quiet --nolock {job.output}
exit 0
