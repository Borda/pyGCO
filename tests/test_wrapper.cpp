#include "cgco.h"
#include <stdio.h>

int main()
{
    int handle;
    int unary[4][3] = {
        {2, 8, 8},
        {7, 3, 7},
        {8, 8, 2},
        {6, 4, 6}
    };

    int edge1[3] = {0, 1, 2};
    int edge2[3] = {1, 2, 3};
    int edge_weight[3] = {3, 10, 1};
    int smooth_cost[3][3] = {
        {0, 1, 1},
        {1, 0, 1},
        {1, 1, 0}
    };
    int n_sites = 4, n_labels = 3, n_edges = 3;
    int labels[3] = {0};
    long long energy = 0;
    int i = 0;

    int handle2;

    gcoCreateGeneralGraph(n_sites, n_labels, &handle);

    gcoCreateGeneralGraph(10, 20, &handle2);
    gcoDestroyGraph(handle2);

    gcoSetDataCost(handle, (int*)unary);

    gcoSetAllNeighbors(handle, edge1, edge2, edge_weight, n_edges);
    gcoSetSmoothCost(handle, (int*)smooth_cost);

    /*
    unary[0][0] = 12345;
    unary[1][0] = 23456;
    unary[2][0] = 78903;
    unary[3][0] = 11111;
    */

    gcoExpansion(handle, 10, &energy);
    gcoGetLabels(handle, labels);

    printf("labels = [ ");
    for (i = 0; i < n_sites; i++)
        printf("%d ", labels[i]);
    printf("], energy=%lld\n", energy);
    gcoComputeDataEnergy(handle, &energy);
    printf("data energy=%lld, ", energy);
    gcoComputeSmoothEnergy(handle, &energy);
    printf("smooth energy=%lld\n", energy);

    gcoDestroyGraph(handle);

    return 0;
}
