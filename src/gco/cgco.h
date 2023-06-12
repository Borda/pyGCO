#ifndef __CGCO_H__
#define __CGCO_H__

#if defined(_MSC_VER)
    #define EXPORT __declspec(dllexport)
#else
    #define EXPORT
#endif

#include "GCoptimization.h"

typedef GCoptimization::LabelID LabelID;
typedef GCoptimization::SiteID SiteID;
typedef GCoptimization::EnergyType EnergyType;
typedef GCoptimization::EnergyTermType EnergyTermType;

/**
 * Create a new general graph. Return an integer handle, which will be used as
 * the reference for the created graph instance.
 */
extern "C" EXPORT int gcoCreateGeneralGraph(SiteID numSites, LabelID numLabels, int *handle);

/**
 * Destroy a graph instance referenced by given handle.
 */
extern "C" EXPORT int gcoDestroyGraph(int handle);

/**
 * Set data cost.
 *
 * unary should be an array of size numSites*numLabels stored in row major
 * order, so that dataCost(s, l) = unary[s*numLabels + l]
 */
extern "C" EXPORT int gcoSetDataCost(int handle, EnergyTermType *unary);

/**
 * Set data cost dataCost(site, label)=e.
 */
extern "C" EXPORT int gcoSetSiteDataCost(int handle, SiteID site, LabelID label, EnergyTermType e);

/**
 * Create an edge betwen s1 and s2 with weight e. s1 should be smaller than s2.
 */
extern "C" EXPORT int gcoSetNeighborPair(int handle, SiteID s1, SiteID s2, EnergyTermType e);

/**
 * Setup the whole neighbor system.
 *
 * s1, s2 and e are vectors of length nPairs. After the call, edge
 * (s1[i], s2[i]) will have weight e[i]
 *
 * Each element of s1 should be smaller than the corresponding element in s2,
 * otherwise the edge is ignored.
 */
extern "C" EXPORT int gcoSetAllNeighbors(int handle, SiteID *s1, SiteID *s2, EnergyTermType *e, int nPairs);

/**
 * Set the smooth cost.
 *
 * e is an array of size numLabels*numLabels, it should be symmetric. So either
 * row-major order or column-major order will be fine.
 *
 * smoothCost(l1, l2) = e[l1*numLabels + l2] = e[l2*numLabels + l1]
 */
extern "C" EXPORT int gcoSetSmoothCost(int handle, EnergyTermType *e);

/**
 * Set the smooth cost for a single pair of labels.
 *
 * smoothCost(l1, l2) = e
 */
extern "C" EXPORT int gcoSetPairSmoothCost(int handle, LabelID l1, LabelID l2, EnergyTermType e);

/**
 * Set a smooth cost function given a pair of sites with corresponding labels.
 */
extern "C" EXPORT int gcoSetSmoothCostFunction(int handle, EnergyTermType (*fun)(SiteID, SiteID, LabelID, LabelID));

/**
 * Do alpha-expansion for a specified number of iterations.
 *
 * Return the total energy after the expansion moves.
 *
 * If maxNumIters is set to -1, it will run until convergence.
 */
extern "C" EXPORT int gcoExpansion(int handle, int maxNumIters, EnergyType *e);

/**
 * Do a single alpha-expansion step on a single label.
 *
 * Return true if the energy is decreased and false otherwise.
 */
extern "C" EXPORT int gcoExpansionOnAlpha(int handle, LabelID label, int *success);

/**
 * Do alpha-beta swap for a specified number of iterations.
 *
 * Return the total energy after the swap moves.
 *
 * If maxNumIters is set to -1, it will run until convergence.
 */
extern "C" EXPORT int gcoSwap(int handle, int maxNumIters, EnergyType *e);

/**
 * Do a single alpha-beta swap for a single pair of labels.
 */
extern "C" EXPORT int gcoAlphaBetaSwap(int handle, LabelID l1, LabelID l2);

/**
 * Compute the total energy for the current label assignments.
 */
extern "C" EXPORT int gcoComputeEnergy(int handle, EnergyType *e);

/**
 * Compute the data energy for the current label assignments.
 */
extern "C" EXPORT int gcoComputeDataEnergy(int handle, EnergyType *e);

/**
 * Compute the smooth energy for the current label assignments.
 */
extern "C" EXPORT int gcoComputeSmoothEnergy(int handle, EnergyType *e);

/**
 * Get the label assignment for the specified site.
 */
extern "C" EXPORT int gcoGetLabelAtSite(int handle, SiteID site, LabelID *label);

/**
 * Get label assignments for all sites. After the call, labels[i] will be the
 * label assignment for site i.
 */
extern "C" EXPORT int gcoGetLabels(int handle, LabelID *labels);

/**
 * Initialize the label of a specified site to a specified label.
 */
extern "C" EXPORT int gcoInitLabelAtSite(int handle, SiteID site, LabelID label);

#endif // __CGCO_H__
