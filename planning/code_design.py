################################################################################################
#       ENVIRONMENT                                                                            #
################################################################################################
class Body:
   """Models Sun, planets and spacecraft"""
   position: Vector3
   mass: double

   # List of all sources originating from this body
   # For sun: PointRadiationSourceInterface for direct solar radiation
   # For planets: PaneledRadiationSourceInterface for albedo + thermal radiation
   # For spacecraft: -
   radiationSourceInterface: RadiationSourceInterface

   # Target interface (for bodies undergoing radiation pressure acceleration)
   # For sun: -
   # For planets: -
   # For spacecraft: CannonballRadiationPressureTargetInterface or
   #    PaneledRadiationPressureTargetInterface
   radiationPressureTargetInterface: RadiationPressureTargetInterface

   temperatureDistribution: TemperatureDistribution  # possible make this a body property
                                                     # for thermal radiation


class RadiationPressureAcceleration(AccelerationModel3d):
   """
   Radiation pressure acceleration from a single source onto a single target.
   """
   source: Body  # e.g. Sun
   target: Body  # e.g. LRO
   occultingBodies: list[Body]  # e.g. Earth and Moon

   def updateMembers(currentTime: double) -> void:
      """"Evaluate radiation pressure acceleration at current time step"""
      force = Vector3.Zero()
      # Iterate over all source panels and their fluxes
      for sourceIrradiance, sourceCenter in source.radiationSourceInterface \
                                 .evaluateIrradianceAtPosition(target.position): # i=1..m
         sourceToTargetDirection = (target.position - sourceCenter).normalize()
         sourceIrradiance *= calculateShadowFunction(source, occultingBodies, target)
         force += target.evaluateRadiationPressureForce(sourceIrradiance,
                                                         sourceToTargetDirection)
      currentAcceleration = force / target.mass


def calculateShadowFunction(occultedBody: Body, occultingBodies: list[Body], \
                              targetBody: Body) -> double:
   # Calculate using Montenbruck 2000 or Zhang 2019 equations
   # Compared to current function in Tudat, takes multiple occulting bodies


abstract class ReflectionLaw:
   # Models a constant BRDF
   def evaluateReflectedFraction(surfaceNormal: Vector3, incomingDirection: Vector3,
                                 observerDirection: Vector3) -> double:
      # Calculate azimuth/polar angles for incoming and observer directions
      # Evaluate BRDF
      reflectedFraction = ...  # [1 / sr]
      return reflectedFraction


class LambertianReflectionLaw(ReflectionLaw):
   reflectance: double  # identical with albedo

   def evaluateReflectedFraction(surfaceNormal: Vector3, incomingDirection: Vector3,
                                 observerDirection: Vector3) -> double:
      return reflectance / PI


################################################################################################
#       SOURCES                                                                                #
################################################################################################

abstract class RadiationSourceInterface:
   source: Body  # The source that this interface belongs to
                 # For albedo, this is the reflecting body, not the Sun

   def evaluateIrradianceAtPosition(targetPosition: Vector3) -> list[tuple[double, Vector3]]:
      """
      Calculate irradiance at target position, also return source position. Subclasses
      are aware of source geometry. Return a list of tuples of flux and origin to
      support multiple fluxes with different origins for paneled sources.
      """
      pass


#===============================================================================================
#       Point radiation source
#===============================================================================================
class PointRadiationSourceInterface(RadiationSourceInterface):
   """Point source (for Sun)"""
   radiantPowerModel: RadiantPowerModel

   def evaluateIrradianceAtPosition(targetPosition: Vector3) -> list[tuple[double, Vector3]]:
      sourcePosition = source.position
      distanceSourceToTarget = (targetPosition - sourcePosition).norm()
      radiantPower = radiantPowerModel.evaluateRadiantPower()
      irradiance = radiantPower / (4 * PI * distanceSourceToTarget**2)  # Eq. 1
      return [(irradiance, sourcePosition)]


abstract class RadiantPowerModel:
   """Gives radiant power for a point source"""

   def evaluateRadiantPower() -> double:
      pass


class GivenRadiantPowerModel(RadiantPowerModel):
   """Gives radiant power directly"""
   radiantPower: double

   def evaluateRadiantPower():
      return radiantPower


class IrradianceRadiantPowerModel(RadiantPowerModel):
   """Gives radiant power from irradiance at certain distance (e.g., TSI at 1 AU)"""
   irradianceAtDistance: double  # could also be a time series from TSI observations
   distance: double

   def evaluateRadiantPower():
      radiantPower = irradianceAtDistance * 4 * PI * distance
      return radiantPower


#===============================================================================================
#       Paneled radiation source
#===============================================================================================
class PaneledRadiationSourceInterface(RadiationSourceInterface):
   """Paneled sphere (for planet albedo + thermal radiation)"""
   originalSource: Body  # Usually the Sun, from where incoming radiation originates
   occultingBodies: list[Body]  # For Moon as source, only Earth occults

   panels: list[SourcePanel]

   def _generatePanels():
      # Panelize body and evaluate albedo for panels. For static paneling
      # (independent of spacecraft position), generate once at start of simulation,
      # Query SH albedo model here if available here, or load albedos and
      # emissivities from file
      panels = ...

   def evaluateIrradianceAtPosition(targetPosition: Vector3) -> list[tuple[double, Vector3]]:
      # For dynamic paneling (depending on target position, spherical cap centered
      # at subsatellite point as in Knocke 1988), could regenerate panels here
      # (possibly with caching), or create separate class
      ret = []
      for panel in panels: # i=1..m
         if not isVisible(panel, targetPosition):
            # Panel hidden at target position
            break

         sourcePosition = panel.absoluteCenter
         distanceSourceToTarget = (targetPosition - sourcePosition).norm()

         irradiance = 0
         for radiationModel in panel.radiationModels:
            irradiance += radiationModel.evaluateIrradianceAtPosition()

         ret.append((irradiance, sourcePosition))
      return ret


class RadiationSourcePanel:
   area: double
   relativeCenter: Vector3  # Panel center relative to source center
   absoluteCenter: Vector3  # Panel center relative to global origin
   normal: Vector3

   radiationModels: list[RadiationModel]


abstract class RadiationModel:
   def evaluateIrradianceAtPosition(panel: RadiationSourcePanel, targetPosition: Vector3) \
         -> double:
      pass

   def getIsotropicEmittedToReceivedIrradianceFactor():
      return dA * cos(alpha) / (4 * PI * r**2)


class AlbedoRadiationModel(RadiationModel):
   reflectionLaw: ReflectionLaw  # usually LambertianReflectionLaw

   def evaluateIrradianceAtPosition(panel: RadiationSourcePanel, targetPosition: Vector3) \
         -> double:
      # for received radiation at panel
      shadowFunction = calculateShadowFunction(originalSource, occultingBodies, panel.center)

      reflectedFraction = reflectionLaw.evaluateReflectedFraction(panel.normal,
         originalSourceDirection, targetDirection)
      albedoIrradiance = \
         shadowFunction * panel.albedo * ...  # albedo radiation calculation, Eq. 2
      return albedoIrradiance


class KnockeThermalRadiationModel(RadiationModel):
   def evaluateIrradianceAtPosition(panel: RadiationSourcePanel, targetPosition: Vector3) \
         -> double:
      thermalIrradiance = panel.emissivity * ...  # thermal radiation calculation, Eq. 3
      return thermalIrradiance


class LemoineThermalRadiationModel(RadiationModel):
   def evaluateIrradianceAtPosition(panel: RadiationSourcePanel, targetPosition: Vector3) \
         -> double:
      temperature = max(...)
      thermalIrradiance = panel.emissivity * ...  # thermal radiation calculation, Eq. 4
      return thermalIrradiance


class ObservedRadiationModel(RadiationModel):
   """Based on measured fluxes (e.g. from CERES, also requires angular distribution model)"""
   def evaluateIrradianceAtPosition(targetPosition: Vector3):
      # 


################################################################################################
#       TARGETS                                                                                #
################################################################################################

abstract class RadiationPressureTargetInterface:
   def evaluateRadiationPressureForce(sourceIrradiance: double,
                                      sourceToTargetDirection: Vector3):
      """
      Calculate radiation pressure force due to a single source panel onto whole target
      """
      pass


class CannonballRadiationPressureTargetInterface(RadiationPressureTargetInterface):
   area: double
   coefficient: double

   def evaluateRadiationPressureForce(sourceIrradiance: double,
                                      sourceToTargetDirection: Vector3):
      force = sourceIrradiance * area * coefficient * ...
      return force


class PaneledRadiationPressureTargetInterface(RadiationPressureTargetInterface):
   panels: List[TargetPanel]

   def evaluateRadiationPressureForce(sourceIrradiance: double,
                                      sourceToTargetDirection: Vector3):
      force = Vector3.Zero()
      for panel in panels: # j=1..n
         if not isVisible(panel, sourceToTargetDirection):
            # Panel pointing away from source
            break

         force += sourceIrradiance * panel.area * ...
      return force


class TargetPanel:
   area: double
   normal: Vector3

   absorptivity: double
   specularReflectivity: double
   diffuseReflectivity: double
   reflectionLaw: ReflectionLaw
