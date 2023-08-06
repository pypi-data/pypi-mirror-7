int unshare(int flags);
int setns(int fd, int nstype);
static const int CLONE_FILES;
static const int CLONE_FS;
static const int CLONE_NEWIPC;
static const int CLONE_NEWNET;
static const int CLONE_NEWNS;
static const int CLONE_NEWUTS;
static const int CLONE_SYSVSEM;
