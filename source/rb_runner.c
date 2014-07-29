/*
 * Modified from FuZhouYiZhong Online Judge
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <dirent.h>
#include <sys/stat.h>
#include <sys/resource.h>
#include <sys/wait.h>
#include <sys/types.h>
#include <signal.h>
inline float tv2s(struct timeval tv)
{
	return (float)tv.tv_usec / 1000000 + tv.tv_sec;
}
int main(int argc, char **argv)
{
	/* Argv 1: Timelimit
	 * Argv 2: INputFile */
	pid_t pid;
	int infd, outfd, errfd;
	char *args[] = { NULL }, *envs[] = { NULL };
	char *cmd = "./Main.rb";
	struct rlimit rtime;
	int status;
	struct rusage usage;
	FILE *get_run_id;
	int run_uid, run_gid, uj_uid, uj_gid;

	get_run_id = popen("id -u nobody", "r");
	fscanf(get_run_id, "%d", &run_uid);
	pclose(get_run_id);
	get_run_id = popen("id -g nobody", "r");
	fscanf(get_run_id, "%d", &run_gid);
	pclose(get_run_id);

	uj_uid = getuid();
	uj_gid = getgid();
	rtime.rlim_cur = rtime.rlim_max = atol(argv[1]) + 1;

	//if (geteuid() == 0) rchown(".");
	pid = fork();
	if (pid == 0) {
		infd = open(argv[2], O_RDONLY);
		dup2(infd, STDIN_FILENO);
		close(infd);
		outfd = open("_tmp_output", O_WRONLY | O_CREAT);
		chmod("_tmp_output", 0666);
		dup2(outfd, STDOUT_FILENO);
		close(outfd);
		errfd = open("_tmp_errmsg", O_WRONLY | O_CREAT);
		chmod("_tmp_errmsg", 0666);
		dup2(outfd, STDERR_FILENO);
		close(errfd);
		/*if (geteuid() == 0) {
			chroot("."); chdir("/");
			chmod("/", 0777);
			setgid(run_gid);
			setuid(run_uid);
		}*/
		setrlimit(RLIMIT_CPU, &rtime);
		execve(cmd, args, envs);
		exit(255);
	}
	else {
		wait4(RUSAGE_CHILDREN, &status, WUNTRACED, &usage);
		printf("%d %d %d %d %d %f %d\n", WIFEXITED(status), WEXITSTATUS(status), WIFSIGNALED(status), WTERMSIG(status), WCOREDUMP(status),
				tv2s(usage.ru_utime) + tv2s(usage.ru_stime),
				(int)usage.ru_maxrss);
	}
	return 0;
}

