#include <errno.h>
#include <float.h>
#include <stdint.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <sys/types.h>
#include <time.h>
#include <unistd.h>
#include <linux/ptp_clock.h>

struct timespec get_ptp_time(char *DEVICE)
{
    #define CLOCKFD 3
    #define FD_TO_CLOCKID(fd)   ((~(clockid_t) (fd) << 3) | CLOCKFD)
    #define CLOCKID_TO_FD(clk)  ((unsigned int) ~((clk) >> 3))
    char *device = DEVICE;
    int fd;
    struct timespec ts;
    clockid_t clkid;
    fd = open(device, O_RDWR);
    if (fd < 0) {
        fprintf(stderr, "opening %s: %s\n", device, strerror(errno));
        exit(0);
    }
    clkid = FD_TO_CLOCKID(fd);
    if (clock_gettime(clkid, &ts)) {
        perror("clock_gettime");
        exit(0);
    }
    else {
        //printf("ptp time in the routine: \n");
        //printf("clock time: %ld.%09ld or %s",
                //ts.tv_sec, ts.tv_nsec, ctime(&ts.tv_sec));
        //clock_gettime(CLOCK_REALTIME, &end);
        //diff = BILLION * (end.tv_sec - start.tv_sec) + end.tv_nsec - start.tv_nsec;
        //printf("elapsed time in the routine = %llu nanoseconds\n", (long long unsigned int) diff);
        close(fd);
        return ts;
    }
}
