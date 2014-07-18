/*
 * Problem: Cirno's Perfect Math Class @ Magimagi
 * Solution: Ans = (N + 1) - PI(DIGITS) - ('10', '11', '20', '21') * PI(DIGITS OF OTHERS)
 * Author: Magimagi
 * Date: 2014-5-12
 */
#include <cstdio>
#include <cstring>
#include <cstdlib>
char Input[50005];
int Trans[50005], Cnt[50];
inline int max(int a, int b)
{
	return a > b ? a : b;
}
class BigNum
{
public:
	int Num[50005];
	int Length;
	int Remainder;
	int& operator [](int x) { return Num[x]; }
	BigNum()
	{
		memset(Num, 0, sizeof(Num));
		Length = 0;
	}
	BigNum(char* Input)
	{
		memset(Num, 0, sizeof(Num));
		Length = strlen(Input);
		for (int i = 1; i <= Length; ++i)
			Num[i] = Input[Length - i] - '0';
	}
	BigNum& operator *=(int x)
	{
		for (int i = 1; i <= Length; ++i)
			Num[i] *= x;
		for (int i = 1; i <= Length; ++i)
			if (Num[i] > 9) {
				if (i == Length)
					++Length;
				Num[i + 1] += Num[i] / 10;
				Num[i] %= 10;
			}
		return *this;
	}
	BigNum& operator /=(int x)
	{
		Remainder = 0;
		for (int i = Length; i > 0; --i) {
			Num[i] += Remainder * 10;
			Remainder = Num[i] % x;
			Num[i] /= x;
			if (i == Length && Num[i] == 0)
				--Length;
		}
		return *this;
	}
	BigNum& Inc()
	{
		Length = max(1, Length);
		++Num[1];
		for (int i = 1; i <= Length; ++i) {
			if (Num[i] > 9) {
				Num[i] -= 10;
				++Num[i + 1];
				if (i == Length)
					++Length;
			}
		}
		return *this;
	}
	void Println()
	{
		if (Length == 0)
			printf("0");
		else
			for (int i = Length; i > 0; --i)
				printf("%d",Num[i]);
		puts("");
	}
};
BigNum operator *(BigNum A, int B)
{
	BigNum Res;
	if (B == 0)
		return Res;
	Res.Length = A.Length;
	for (int i = 1; i <= Res.Length; ++i)
		Res[i] = A[i] * B;
	for (int i = 1; i <= Res.Length; ++i)
		if (Res[i] > 9) {
			if (i == Res.Length)
				++Res.Length;
			Res[i + 1] += Res[i] / 10;
			Res[i] %= 10;
		}
	return Res;
}
BigNum operator *(BigNum A, BigNum B)
{
	BigNum Res;
	Res.Length = A.Length + B.Length - 1;
	for (int i = 1; i <= A.Length; ++i)
		for (int j = 1; j <= B.Length; ++j)
			Res[i + j - 1] += A[i] * B[j];
	for (int i = 1; i <= Res.Length; ++i)
		if (Res[i] > 9) {
			Res[i + 1] += Res[i] / 10;
			Res[i] %= 10;
			if (i == Res.Length)
				++Res.Length;
		}
	return Res;
}
BigNum operator -(BigNum A, BigNum B)
{
	BigNum Res;
	Res.Length = max(A.Length, B.Length);
	for (int i = 1; i <= Res.Length; ++i) {
		Res[i] += A[i] - B[i];
		if (Res[i] < 0) {
			Res[i] += 10;
			--Res[i + 1];
		}
	}
	while (Res.Length > 0 && Res[Res.Length] == 0)
		--Res.Length;
	return Res;
}
BigNum Power(int Base, int P)
{
	char one[] = "1";
	BigNum Now(one);
	if (P <= 0)
		return Now;
	for (int i = 1; i <= P; ++i)
		Now *= Base;
	return Now;
}
BigNum Eval()
{
	memset(Cnt, 0, sizeof(Cnt));
	memset(Trans, 0, sizeof(Trans));
	BigNum N(Input);
	BigNum T = N;
	if (N.Length == 1 && N[1] == 0)
		return N;
	int Tail = 0;
	while (T.Length != 0) {
		T /= 3;
		++Cnt[Trans[++Tail] = T.Remainder];
	}
	int A = 0, // 10
		B = 0, // 11
		C = 0, // 20
		D = 0; // 21
	for (int i = Tail; i > 1; --i)
		if (Trans[i] == 1 && Trans[i - 1] == 0)
			A += 2;
		else if (Trans[i] == 1 && Trans[i - 1] == 1)
			B += 1;
		else if (Trans[i] == 2 && Trans[i - 1] == 0)
			C += 4;
		else if (Trans[i] == 2 && Trans[i - 1] == 1)
			D += 2;
	BigNum DDPower2, DPower2, Power2, DPower3, Power3;
	DDPower2 = Power(2, Cnt[1] - 2);
	if (Cnt[1] <= 1)
		DPower2 = DDPower2;
	else
		DPower2 = DDPower2 * 2;
	if (Cnt[1] <= 0)
		Power2 = DPower2;
	else
		Power2 = DPower2 * 2;
	DPower3 = Power(3, Cnt[2] - 1);
	if (Cnt[2] <= 0)
		Power3 = DPower3;
	else
		Power3 = DPower3 * 3;
	return N.Inc() - Power2 * Power3
				   - DPower2 * Power3 * A
				   - DDPower2 * Power3 * B
				   - Power2 * DPower3 * C
				   - DPower2 * DPower3 * D;
}
int main()
{
	int T, N;
	for (scanf("%d\n", &T); T; --T) {
		scanf("%s", Input);
		Eval().Println();
	}
	return 0;
}