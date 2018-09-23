

#pragma GCC optimize(3,"Ofast","inline")
#include<algorithm>
#include<vector>
#include<climits>
#include<cfloat>
#include <iostream>
#include <string>
#include <fstream>
#include <sstream>


//---------------------

// Input consists of some lines of:
// id month1 month2 month3 month4 month5 month6 month_predict
// eg: 000068 -0.00027 -0.00587 -0.00071 -0.00350 0.00078 -0.01578 0.11213

using namespace std;
// S: size of searching space
// N: number of selected gupiaos
const int S = 25, N = 10;

// VaR = -mu(T) - C * Sigma(T)
// s.t k1x1+k2x2+...k10x10 >= lower_bound_profit, mini: VaR
// s.t VaR <= upper_bound_VaR, maxi: k1x1+k2x2+...k10x10
const double C = -1.6448536269514729;
const double lower_bound_profit = 0.0300;
const double upper_bound_VaR = 0.0020;

struct Node{
    char id[10];
    double profit[7];
    bool operator < (const Node& rhs) const {
        return profit[6] > rhs.profit[6];
    }
};
vector<Node> input;
void readin(){
    Node x;
    while (scanf("%s", x.id) != EOF) {
        for (int i = 0; i < 7; i++) scanf("%lf", &x.profit[i]);
        input.push_back(x);
    }
    sort(input.begin(), input.end());
    input.erase(input.begin() + N, input.end());
}

vector<vector<double> > Vec;
vector<double> vec;
void generate_arr(int n = 0, int tot = 0){
    if (tot == S) return;
    if (n == N - 1) {
        vec.push_back((S - tot) / double(S));
        Vec.push_back(vec);
        vec.pop_back();
        return;
    }
    for (int i = 1; i <= S - tot; i++) {
        vec.push_back(i / double(S));
        generate_arr(n + 1, tot + i);
        vec.pop_back();
    }
}

double get_VaR(vector<double>& r) {
    double VaR = 0.0, bar = 0.0;
    int n = 6;
    for (int i = 0; i < n; i++) bar += r[i];
    bar /= double(n);
    for (int i = 0; i < n; i++) VaR += (r[i] - bar) * (r[i] - bar);
    return -bar - C * VaR / double(n);
}

void output_mini_VaR(){
    // getting min_VaR, s.t profit >= lower_bound_profit
    int best_idx = -1; double min_VaR = DBL_MAX;
    vector<double> r(7);
    for (int i = 0; i < Vec.size(); i++) {
        if (i % 5000000 == 0) printf("cnt = %d\n", i);

        vector<double> &arr_k = Vec[i];
        for (int idx = 0; idx < 7; idx++){
            r[idx] = 0.0;
            for (int i = 0; i < N; i++) {
                r[idx] += input[i].profit[idx] * arr_k[i];
            }
        }
        if (r[6] < lower_bound_profit) continue;
        else {
            double cur_VaR = get_VaR(r);
            if (cur_VaR < min_VaR) min_VaR = cur_VaR, best_idx = i;
        }
    }
    if (best_idx == -1) {
        puts("Impossible to satisfy!\n");
    } else {
        ofstream outFile;
        outFile.open("stockchoice.csv", ios::app); // 打开模式可省略
        outFile << "0.03" <<',';
        outFile << min_VaR << ',';
        for (int i = 0; i < N-1; i++)
        {
        outFile << input[i].id << ','<<Vec[best_idx][i]<<',';
        }
        outFile << input[N-1].id << ','<<Vec[best_idx][N-1];
        outFile.close();
    }
}

void output_maxi_profit(){
    // getting max_profit, s.t VaR <= upper_bound_VaR
    int best_idx = -1; double max_profit = DBL_MIN;
    vector<double> r(7);
    for (int i = 0; i < Vec.size(); i++) {
        if (i % 5000000 == 0) printf("cnt = %d\n", i);

        vector<double> &arr_k = Vec[i];
        for (int idx = 0; idx < 7; idx++){
            r[idx] = 0.0;
            for (int i = 0; i < N; i++) {
                r[idx] += input[i].profit[idx] * arr_k[i];
            }
        }
        double cur_VaR = get_VaR(r);
        if (cur_VaR > upper_bound_VaR) continue;
        else {
            if (r[6] > max_profit) max_profit = r[6], best_idx = i;
        }
    }
    if (best_idx == -1) {
        puts("Impossible to satisfy!\n");
    } else {
        ofstream outFile;
        outFile.open("stockchoice.csv", ios::out); // 打开模式可省略
        outFile << "Profit" << ',' << "VaR" << ',' << "Id1"<< ',' <<"K1"<< ','<< "Id2" << ','<<"K2"<< ','<< "Id3" << ','<<"K3"<< ','<< "Id4"<< ',' <<"K4"<< ','<< "Id5" << ','<<"K5"<< ','<< "Id6" << ','<<"K6"<< ','<< "Id7" << ','<<"K7"<< ','<< "Id8"<< ',' <<"K8"<< ','<< "Id9" << ','<<"K9"<< ','<< "Id10" << ','<<"K10"<<endl;
        outFile << max_profit <<',';
        outFile << "0.002" << ',';
        for (int i = 0; i < N-1; i++)
        {
        outFile << input[i].id << ','<<Vec[best_idx][i]<<',';
        }
        outFile << input[N-1].id << ','<<Vec[best_idx][N-1]<<endl;
        outFile.close();

        // printf("best_idx = %d, max_profit = %.15f\n", best_idx, max_profit);
        // for (int i = 0; i < N; i++) printf("%s: %f\n", input[i].id, Vec[best_idx][i]);
    }
}

int main(){

    freopen("profit", "r", stdin);
    readin();
    generate_arr();
    printf("Searching size is %d\n", Vec.size());

    printf("getting min_VaR, s.t profit >= %f\n", lower_bound_profit);
    output_maxi_profit();
    output_mini_VaR();
}
