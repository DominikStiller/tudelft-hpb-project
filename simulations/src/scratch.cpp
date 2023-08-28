#include <iostream>
#include <fstream>
#include <vector>

#include <Eigen/Core>

#include "tudat/simulation/simulation.h"
#include "tudat/astro/basic_astro/celestialBodyConstants.h"
#include "tudat/astro/basic_astro/sphericalBodyShapeModel.h"

using namespace tudat;
using namespace tudat::electromagnetism;
using namespace tudat::simulation_setup;
using namespace tudat::unit_conversions;
using namespace tudat::ephemerides;
using namespace tudat::basic_astrodynamics;



// Calculate albedo values for one orbit revolution
void albedo()
{
    spice_interface::loadStandardSpiceKernels( );

    const auto globalFrameOrigin = "Earth";
    const auto globalFrameOrientation = "J2000";
    const auto bodySettings = getDefaultBodySettings({"Earth", "Sun"}, globalFrameOrigin, globalFrameOrientation);
    auto bodies = createSystemOfBodies(bodySettings);
    setGlobalFrameBodyEphemerides(bodies.getMap(), globalFrameOrigin, globalFrameOrientation);

    /*
     * Once scratch is periodic, compare values using debugging with v&v (verification_validation.ipynb?)
     */

    const auto originalSourceModelSettings = bodySettings.at("Sun")->radiationSourceModelSettings;
    const auto originalSourceModel =
            std::dynamic_pointer_cast<IsotropicPointRadiationSourceModel>(createRadiationSourceModel(originalSourceModelSettings, "Sun", bodies));
    const auto originalSourceBodyShapeModel = bodies.at("Sun")->getShapeModel();

    const auto targetModelSettings = cannonballRadiationPressureTargetModelSettings(0.28483, 1.13);
    const auto targetModel = createRadiationPressureTargetModel(targetModelSettings, "Vehicle", bodies);

    const auto sourceModelSettings = dynamicallyPaneledRadiationSourceModelSettings("Sun", {
                    albedoPanelRadiosityModelSettings(SecondDegreeZonalPeriodicSurfacePropertyDistributionModel::albedo_knocke),
//                    delayedThermalPanelRadiosityModelSettings(SecondDegreeZonalPeriodicSurfacePropertyDistributionModel::emissivity_knocke)
            }, {6, 12});
//            }, {24, 36, 48, 60, 72, 84, 96, 108});
//    const auto sourceModelSettings = staticallyPaneledRadiationSourceModelSettings("Sun", {
//                    albedoPanelRadiosityModelSettings(SecondDegreeZonalPeriodicSurfacePropertyDistributionModel::albedo_knocke),
////                    delayedThermalPanelRadiosityModelSettings(SecondDegreeZonalPeriodicSurfacePropertyDistributionModel::emissivity_knocke)
//            }, 2000);
    const auto sourceModel =
            std::dynamic_pointer_cast<PaneledRadiationSourceModel>(createRadiationSourceModel(sourceModelSettings, globalFrameOrigin, bodies));

    const auto albedoSettings = secondDegreeZonalPeriodicSurfacePropertyDistributionSettings(SecondDegreeZonalPeriodicSurfacePropertyDistributionModel::albedo_knocke);
//    const auto albedoSettings = secondDegreeZonalPeriodicSurfacePropertyDistributionSettings(SecondDegreeZonalPeriodicSurfacePropertyDistributionModel::emissivity_knocke);
    const auto albedoModel = createSurfacePropertyDistribution(albedoSettings, globalFrameOrigin);

//    Eigen::Vector6d initialStateInKeplerianElements = Eigen::Vector6d::Zero( );
//    initialStateInKeplerianElements[ 0 ] = 8000E3;
//    initialStateInKeplerianElements[ orbital_element_conversions::inclinationIndex ] = convertDegreesToRadians( 90.0 );
//    initialStateInKeplerianElements[ orbital_element_conversions::argumentOfPeriapsisIndex ] = convertDegreesToRadians( -90.0 );
//    initialStateInKeplerianElements[ orbital_element_conversions::longitudeOfAscendingNodeIndex ] = convertDegreesToRadians( 0 );
//    const auto ephemerisSettings =
//            keplerEphemerisSettings(
//                    initialStateInKeplerianElements,
//                    0.0,
//                    celestial_body_constants::EARTH_GRAVITATIONAL_PARAMETER,
//                    globalFrameOrigin, globalFrameOrientation);
//    const auto ephemeris = createBodyEphemeris(ephemerisSettings, globalFrameOrigin);
//
//    radiationSourceModel->updateMembers(
//            spice_interface::convertDateStringToEphemerisTime("2010 JAN 1"));
//    albedoModel->updateMembers(
//            spice_interface::convertDateStringToEphemerisTime("2010 JAN 1"));

    // Epoch: 16 Feb 1977
    const auto tle = std::make_shared<Tle>(
            "1 08820U 76039  A 77047.52561960  .00000002 +00000-0 +00000-0 0  9994\n"
            "2 08820 109.8332 127.3884 0044194 201.3006 158.6132 06.38663945018402");
    auto tleEphemeris = std::make_shared<TleEphemeris>(globalFrameOrigin, globalFrameOrientation, tle);

    const auto startTime = tle->getEpoch() + 0 * 365. / 4 * 24 * 3600;

    Eigen::Vector6d initialStateInKeplerianElements =
            orbital_element_conversions::convertCartesianToKeplerianElements(
                    tleEphemeris->getCartesianState(startTime), celestial_body_constants::EARTH_GRAVITATIONAL_PARAMETER);

    auto ephemeris =
            std::make_shared<KeplerEphemeris>(initialStateInKeplerianElements, startTime,
                            celestial_body_constants::EARTH_GRAVITATIONAL_PARAMETER, globalFrameOrigin, globalFrameOrientation);

    double orbitalPeriod = basic_astrodynamics::computeKeplerOrbitalPeriod(
        initialStateInKeplerianElements[ orbital_element_conversions::semiMajorAxisIndex ],
        celestial_body_constants::EARTH_GRAVITATIONAL_PARAMETER, 0 );

    std::ofstream outfile;
    outfile.open("results/scratch_out.txt");

    const int n_rev = 3;
    const double n_steps_per_rev = 1000;
    for (int i = 0; i <= n_rev * n_steps_per_rev; ++i)
    {
        double t = startTime + i / n_steps_per_rev * orbitalPeriod;

        bodies.at("Earth")->setStateFromEphemeris(t);
        bodies.at("Earth")->setCurrentRotationToLocalFrameFromEphemeris(t);
        bodies.at("Sun")->setStateFromEphemeris(t);

        const Eigen::Quaterniond earthToGlobalRotation = bodies.at("Earth")->getCurrentRotationToGlobalFrame();
        const Eigen::Quaterniond globalToEarthRotation = earthToGlobalRotation.inverse();

        const Eigen::Vector3d position = ephemeris->getCartesianPosition(t);
        const Eigen::Vector3d positionInEarthFrame = globalToEarthRotation * position;
        const Eigen::Vector3d sphericalPosition =
                coordinate_conversions::convertCartesianToSpherical(positionInEarthFrame);
        const Eigen::Vector3d velocity = ephemeris->getCartesianVelocity(t);

        const auto latitude = PI / 2 - sphericalPosition(1);
        const auto longitude = sphericalPosition(2);

        const auto originalSourcePosition = bodies.at("Sun")->getPosition();

        PaneledSourceRadiationPressureAcceleration accelerationModel(
            sourceModel,
            [] () { return Eigen::Vector3d::Zero(); },
            [=] () { return earthToGlobalRotation; },
//            [] () { return Eigen::Quaterniond::Identity(); },
            targetModel,
            [=] () { return position; },
            [] () { return Eigen::Quaterniond::Identity(); },
            [] () { return 406.9; },
            originalSourceModel,
            originalSourceBodyShapeModel,
            [=] () { return originalSourcePosition; },
            std::make_shared<NoOccultingBodyOccultationModel>(),
            std::make_shared<NoOccultingBodyOccultationModel>()
        );

        sourceModel->updateMembers(t);
        albedoModel->updateMembers(t);
        accelerationModel.updateMembers(t);

        const auto albedo = albedoModel->getValue(latitude, longitude);
        const auto acceleration = accelerationModel.getAcceleration();
        const auto irradiance =  accelerationModel.getReceivedIrradiance();
        const auto visibleArea =  accelerationModel.getVisibleSourceArea();
        const auto visiblePanels =  accelerationModel.getVisibleSourcePanelCount();
        const auto illuminatedPanels =  accelerationModel.getIlluminatedSourcePanelCount();
        const auto visibleAndIlluminatedPanels =  accelerationModel.getVisibleAndIlluminatedSourcePanelCount();

        outfile << t << ", " ;
        outfile << position(0) << ", " << position(1) << ", " << position(2) << ", " ;
        outfile << velocity(0) << ", " << velocity(1) << ", " << velocity(2) << ", " ;
        outfile << acceleration(0) << ", " << acceleration(1) << ", " << acceleration(2) << ", " ;
        outfile << albedo << ", " << irradiance << ", " << visibleArea << ", ";
        outfile << visiblePanels << ", " << illuminatedPanels << ", " << visibleAndIlluminatedPanels << std::endl;
    }
    outfile.close();
}

int main()
{
    albedo();
}
