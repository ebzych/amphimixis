<div style="text-align: justify">

# METHODOLOGY FOR EXPLORING PROJECT READINESS FOR MIGRATION TO A DIFFERENT ARCHITECTURE

> This guide assumes maintaining a report to document key findings for each project under study. Nearly every section is highlighted for inclusion in the report

1. Finding the active repository:
   - check the dates of the latest commits and issues
   - review the description and README in case the project was moved to another repository as part of a larger project (e.g., RapidXML moved to Boost); in that case, check if the project can be built standalone, without the parent project
   - check for other repositories maintained and developed by other developers; if two forks evolve in parallel, one version may be more advanced
   - look for stable releases, GitHub version tags, etc.

2. After selecting an active repository, examine its structure and assess maintainability and complexity:
   - presence of tests, CI, build systems, documentation, benchmarks
   - number of dependencies; later, to assess migration suitability, also evaluate dependency readiness
   - presence of vectorization macros and other platform-dependent macros in the code; verify their semantics — macro names can sometimes be misleading

3. To evaluate package behavior on the target architecture, build and verify it on the project target platform (typically x86):
   - build with debug info and optimizations
   - build tests using available methods (usually a config option or build target)
   - verify functionality: run tests; if they fail, consult documentation or issues; document findings; report bugs to developers if not already done (e.g., file an issue or submit a patch)

4. For profiling, use `perf stat` and `perf record`:
   - ensure experimental rigor:
      - Pin the process to a high-performance core (`taskset -c <performance_core_number> <your_executable>` on Linux)
      - Set highest priority (`nice -n -20 <your_executable>` on Linux, requires root)
   - run `perf stat` via the following command

      ```shell
      perf stat -ddd nice -n -20 taskset -c <performance_core_number> <your_executable> # -ddd (triple -d) gives more info
      ```

      From its output, pay attention to elapsed time, cache-misses, branches (branch-misses), and color-highlighted metrics
   - run `perf record` via the command

      ```shell
      perf record nice -n -20 taskset -c <performance_core_number> <your_executable>
      ```

      After collecting samples, view execution statistics with `perf report`
   - compare execution traces across all build variants: run each build at least 6-10 times to get averaged numbers
   - prefer benchmarks over tests for more illustrative results; if test runtime depends on dataset size, try increasing it
   - compare builds for the target architecture against a reference platform; include the comparison in the report

5. Attempt to optimize bottlenecks:
   - use your toolchain's `objdump` to look for platform vector instructions; if none found, try compiler vectorization flags; if that doesn't help, try a newer toolchain (from your distro repos, specialized vendors like Syntacore, or configure one yourself with `crosstool-NG`); if the project has dependencies that need to be separately downloaded into the toolchain root, try `debootstrap` (on Debian-family distros) or `buildroot`
   - try a different memory allocator: jemalloc, tcmalloc, etc.; if the issue involves heavy `free` or `delete` calls, use arena allocators
   - build the project with LTO
   - try optimizing high-load areas identified from `perf report` output

***Share your results, and may the Open Source be with you!***

</div>
