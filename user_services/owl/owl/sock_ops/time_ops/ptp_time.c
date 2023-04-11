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
        return ts;
    }
}

int main(int argc, char *argv[] ) {
    struct timespec ts;

    ts = get_ptp_time(argv[1]);
    printf("%ld.%09ld \n", ts.tv_sec, ts.tv_nsec);
}
