/**
 * Many error checks are not performed because it seems hard to pass these
 * error message back to python.
 *
 * So be careful when using this wrapper, and make sure the parameters in
 * function calls are valid.
 *
 * This wrapper now only supports general graph.  The grid graph is not
 * implemented yet.
 *
 * The return value of all functions are integers, which can be potentially
 * used for error signals. If it is required to return something, the address
 * of the required return value is passed as an argument to the function and
 * it will be filled with the expected return value after the call.
 *
 * Yujia Li, 08/2013
 *
 */

#if defined(_MSC_VER)
    #define EXPORT __declspec(dllexport)
#else
    #define EXPORT
#endif

#include <map>
#include <stdio.h>
#include <stdlib.h>
#include "GCoptimization.h"

typedef GCoptimization::LabelID LabelID;
typedef GCoptimization::SiteID SiteID;
typedef GCoptimization::EnergyType EnergyType;
typedef GCoptimization::EnergyTermType EnergyTermType;

typedef std::map<int, GCoptimization*> GcoInstanceMap;
static GcoInstanceMap _gcoInstanceMap;
static int _gcoNextInstanceId = 12345;

GcoInstanceMap::mapped_type& findInstance(int handle)
{
    GcoInstanceMap::iterator it = _gcoInstanceMap.find(handle);
    if (it != _gcoInstanceMap.end())
        return it->second;
    else
    {
        fprintf(stderr, "Invalid instance handle %d\n", handle);
        exit(EXIT_FAILURE);
    }
}

void removeInstance(int handle)
{
    delete findInstance(handle);
    _gcoInstanceMap.erase(handle);
}

extern "C" EXPORT int gcoCreateGeneralGraph(SiteID numSites, LabelID numLabels, int *handle)
{
    GCoptimization *gco = new GCoptimizationGeneralGraph(numSites, numLabels);
    _gcoInstanceMap[_gcoNextInstanceId] = gco;
    *handle = _gcoNextInstanceId;
    _gcoNextInstanceId++;
    return 0;
}

extern "C" EXPORT int gcoDestroyGraph(int handle)
{
    removeInstance(handle);
    return 0;
}

extern "C" EXPORT int gcoSetDataCost(int handle, EnergyTermType *unary)
{
    GCoptimization *gco = findInstance(handle);
    gco->setDataCost(unary);
    return 0;
}

extern "C" EXPORT int gcoSetSiteDataCost(int handle, SiteID site, LabelID label, EnergyTermType e)
{
    GCoptimization *gco = findInstance(handle);
    gco->setDataCost(site, label, e);
    return 0;
}

extern "C" EXPORT int gcoSetNeighborPair(int handle, SiteID s1, SiteID s2, EnergyTermType e)
{
    GCoptimizationGeneralGraph *gco = (GCoptimizationGeneralGraph*)findInstance(handle);
    if (s1 < s2)
        gco->setNeighbors(s1, s2, e);
    return 0;
}

extern "C" EXPORT int gcoSetAllNeighbors(int handle, SiteID *s1, SiteID *s2, EnergyTermType *e, int nPairs)
{
    GCoptimizationGeneralGraph *gco = (GCoptimizationGeneralGraph*)findInstance(handle);
    for (int i = 0; i < nPairs; i++)
        if (s1[i] < s2[i])
            gco->setNeighbors(s1[i], s2[i], e[i]);
    return 0;
}

extern "C" EXPORT int gcoSetSmoothCost(int handle, EnergyTermType *e)
{
    GCoptimization *gco = findInstance(handle);
    gco->setSmoothCost(e);
    return 0;
}

extern "C" EXPORT int gcoSetPairSmoothCost(int handle, LabelID l1, LabelID l2, EnergyTermType e)
{
    GCoptimization *gco = findInstance(handle);
    gco->setSmoothCost(l1, l2, e);
    return 0;
}

extern "C" EXPORT int gcoSetSmoothCostFunction(int handle, EnergyTermType (*fun)(SiteID, SiteID, LabelID, LabelID))
{
    GCoptimization *gco = findInstance(handle);
    gco->setSmoothCost(fun);
    return 0;
}

extern "C" EXPORT int gcoExpansion(int handle, int maxNumIters, EnergyType *e)
{
    GCoptimization *gco = findInstance(handle);
    *e = gco->expansion(maxNumIters);
    return 0;
}

extern "C" EXPORT int gcoExpansionOnAlpha(int handle, LabelID label, int *success)
{
    GCoptimization *gco = findInstance(handle);
    if (gco->alpha_expansion(label))
        *success = 1;
    else
        *success = 0;
    return 0;
}

extern "C" EXPORT int gcoSwap(int handle, int maxNumIters, EnergyType *e)
{
    GCoptimization *gco = findInstance(handle);
    *e = gco->swap(maxNumIters);
    return 0;
}

extern "C" EXPORT int gcoAlphaBetaSwap(int handle, LabelID l1, LabelID l2)
{
    GCoptimization *gco = findInstance(handle);
    gco->alpha_beta_swap(l1, l2);
    return 0;
}

extern "C" EXPORT int gcoComputeEnergy(int handle, EnergyType *e)
{
    GCoptimization *gco = findInstance(handle);
    *e = gco->compute_energy();
    return 0;
}

extern "C" EXPORT int gcoComputeDataEnergy(int handle, EnergyType *e)
{
    GCoptimization *gco = findInstance(handle);
    *e = gco->giveDataEnergy();
    return 0;
}

extern "C" EXPORT int gcoComputeSmoothEnergy(int handle, EnergyType *e)
{
    GCoptimization *gco = findInstance(handle);
    *e = gco->giveSmoothEnergy();
    return 0;
}

extern "C" EXPORT int gcoGetLabelAtSite(int handle, SiteID site, LabelID *label)
{
    GCoptimization *gco = findInstance(handle);
    *label = gco->whatLabel(site);
    return 0;
}

extern "C" EXPORT int gcoGetLabels(int handle, LabelID *labels)
{
    GCoptimization *gco = findInstance(handle);
    gco->whatLabel(0, gco->numSites(), labels);
    return 0;
}

extern "C" EXPORT int gcoInitLabelAtSite(int handle, SiteID site, LabelID label)
{
    GCoptimization *gco = findInstance(handle);
    gco->setLabel(site, label);
    return 0;
}
