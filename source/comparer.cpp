#include <fstream>
#include <iostream>
using namespace std;
int main(int argc, char* argv[])
{
	/* 1, 2, 3: Input, Output, StdOut */
	ifstream Input(argv[1]), Output(argv[2]), StdOut(argv[3]);
	string A, B;
	bool L, R;
	for (L = R = false; (L = (Output >> A)) && (R = (StdOut >> B)); L = R = false)
		if (A != B) {
			cout << 0 << endl;
			return 0;
		}
	if (L || R)
		cout << 0 << endl;
	else
		cout << 10 << endl;
	return 0;
}
