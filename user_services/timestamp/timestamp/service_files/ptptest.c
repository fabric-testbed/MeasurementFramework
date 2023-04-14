#include "get_ptp_time.c"

int main(void)
{
  struct timespec ts;
  ts = get_ptp_time("/dev/ptp2");
  printf("clock time: %ld.%09ld or %s",
          ts.tv_sec, ts.tv_nsec, ctime(&ts.tv_sec));
}