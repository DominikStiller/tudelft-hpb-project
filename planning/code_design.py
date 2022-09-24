################################################################################################
#       ENVIRONMENT                                                                            #
################################################################################################
class Body:
   """Models Sun, planets and spacecraft"""
   position: Vector3
   mass: double

   # List of all sources originating from this body
   # For sun: PointRadiationSourceModel for direct solar radiation
   # For planets: PaneledRadiationSourceModel for albedo + thermal radiation
   # For spacecraft: -
   radiationSourceModel: RadiationSourceModel

   # Target model (for bodies undergoing radiation pressure acceleration)
   # For sun: -
   # For planets: -
   # For spacecraft: CannonballRadiationPressureTargetModel or
   #    PaneledRadiationPressureTargetModel
   radiationPressureTargetModel: RadiationPressureTargetModel


class RadiationPressureAcceleration(AccelerationModel3d):
   """
   Radiation pressure acceleration from a single source onto a single target.
   """
   source: Body  # e.g. Sun
   target: Body  # e.g. LRO
   occultationModel: OccultationModel

   def updateMembers(currentTime: double) -> void:
      """"Evaluate radiation pressure acceleration at current time step"""

      # rotate target position to source-fixed frame
      irradianceList = source.radiationSourceModel \
                                 .evaluateIrradianceAtPosition(target.position)
      # rotate irradiances to target-fixed frame

      force = Vector3.Zero()
      # Iterate over all source panels and their fluxes
      for sourceIrradiance, sourceCenter in irradianceList: # i=1..m
         sourceToTargetDirection = (target.position - sourceCenter).normalize()
         # rotate sourceToTargetDirection to target-fixed frame
         sourceIrradiance = occultationModel.applyOccultation(sourceIrradiance)
         force += target.evaluateRadiationPressureForce(sourceIrradiance,
                                                         sourceToTargetDirection)
      # rotate force to global frame
      currentAcceleration = force / target.mass


abstract class OccultationModel:
   occultingBodies: list[Body]  # e.g. Earth and Moon

   def applyOccultation(sourceIrradiance: double, occultedBody: Body, targetBody: Body) -> double:
      pass


abstract class ShadowFunctionOccultation:
   def applyOccultation(irradiance: double, occultedBody: Body, targetBody: Body) -> double:
      # Calculate using Montenbruck 2000 or Zhang 2019 equations
      # Compared to current function in Tudat, takes multiple occulting bodies
      shadowFunction = ...
      irradiance *= shadowFunction
      return irradiance


abstract class ReflectionLaw:
   # Models a constant BRDF
   def evaluateReflectedFraction(surfaceNormal: Vector3, incomingDirection: Vector3,
                                 observerDirection: Vector3) -> double:
      # Calculate azimuth/polar angles for incoming and observer directions
      # Evaluate BRDF
      reflectedFraction = ...  # [1 / sr]
      return reflectedFraction

   def evaluateReactionVector(surfaceNormal: Vector3, incomingDirection: Vector3) -> Vector3:
      # integrates Wetterer Eq 2


class LambertianReflectionLaw(ReflectionLaw):
   # Possibly subclass of SpecularDiffuseMixReflectionLaw
   reflectance: double  # identical with albedo

   def evaluateReflectedFraction(surfaceNormal: Vector3, incomingDirection: Vector3,
                                 observerDirection: Vector3) -> double:
      return reflectance / PI


class SpecularDiffuseMixReflectionLaw(ReflectionLaw):
   absorptivity: double
   specularReflectivity: double
   diffuseReflectivity: double

   def evaluateReactionVector(surfaceNormal: Vector3, incomingDirection: Vector3) -> Vector3:
      # evaluates Wetterer Eq 5


################################################################################################
#       SOURCES                                                                                #
################################################################################################

abstract class RadiationSourceModel:
   source: Body  # The source that this model belongs to
                 # For albedo, this is the reflecting body, not the Sun

   def evaluateIrradianceAtPosition(targetPosition: Vector3) -> list[Vector3]:
      """
      Calculate irradiance at target position, also return source position. Subclasses
      are aware of source geometry. Return a list of tuples of flux and origin to
      support multiple fluxes with different origins for paneled sources.
      """
      pass


#===============================================================================================
#       Point radiation source
#===============================================================================================
class IsotropicPointRadiationSourceModel(RadiationSourceModel):
   """Point source (for Sun)"""
   luminosityModel: LuminosityModel

   def evaluateIrradianceAtPosition(targetPosition: Vector3) -> list[tuple[double, Vector3]]:
      sourcePosition = source.position
      distanceSourceToTarget = targetPosition.norm()
      luminosity = luminosityModel.evaluateLuminosity()
      irradiance = luminosity / (4 * PI * distanceSourceToTarget**2)  # Eq. 1
      return [(irradiance, sourcePosition)]


abstract class LuminosityModel:
   """Gives luminosity for a point source"""

   def evaluateLuminosity() -> double:
      pass


class ConstantLuminosityModel(LuminosityModel):
   """Gives luminosity directly"""
   luminosity: double

   def evaluateLuminosity():
      return luminosity


class IrradianceBasedLuminosityModel(LuminosityModel):
   """Gives luminosity from irradiance at certain distance (e.g., TSI at 1 AU)"""
   irradianceAtDistance: double  # could also be a time series from TSI observations
   distance: double

   def evaluateLuminosity():
      luminosity = irradianceAtDistance * 4 * PI * distance**2
      return luminosity


#===============================================================================================
#       Paneled radiation source
#===============================================================================================
class PaneledRadiationSourceModel(RadiationSourceModel):
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
      sourceBodyPosition = source.position

      ret = []
      for panel in panels: # i=1..m
         sourcePosition = sourceBodyPosition + panel.relativeCenter

         irradiance = 0
         for radiationModel in panel.radiationModels:
            irradiance += radiationModel.evaluateIrradianceAtPosition(
               panel, targetPosition)

         ret.append((irradiance, sourcePosition))
      return ret


class RadiationSourcePanel:
   area: double
   relativeCenter: Vector3  # Panel center relative to source center
   normal: Vector3  # body-fixed

   radiationModels: list[PanelRadiationModel]


abstract class PanelRadiationModel:
   def evaluateIrradianceAtPosition(panel: RadiationSourcePanel, targetPosition: Vector3) \
         -> double:
      pass


class AlbedoPanelRadiationModel(PanelRadiationModel):
   # Usually LambertianReflectionLaw
   reflectionLaw: ReflectionLaw

   def evaluateIrradianceAtPosition(panel: RadiationSourcePanel, targetPosition: Vector3) \
         -> double:
      if not isVisible(panel, targetPosition):
            # Panel hidden at target position
            return 0

      # for received radiation at panel
      shadowFunction = calculateShadowFunction(originalSource, occultingBodies, panel.center)

      reflectedFraction = reflectionLaw.evaluateReflectedFraction(panel.normal,
         originalSourceDirection, targetDirection)
      albedoIrradiance = \
         shadowFunction * ...  # albedo radiation calculation, Eq. 2
      return albedoIrradiance


class DelayedThermalPanelRadiationModel(PanelRadiationModel):
   # Based on Knocke (1988)
   emissivity: double
   temperature: double

   def evaluateIrradianceAtPosition(panel: RadiationSourcePanel, targetPosition: Vector3) \
         -> double:
      thermalIrradiance = emissivity * ...  # thermal radiation calculation, Eq. 3
      return thermalIrradiance


class AngleBasedThermalPanelRadiationModel(PanelRadiationModel):
   # Based on Lemoine (2013)
   emissivity: double

   def evaluateIrradianceAtPosition(panel: RadiationSourcePanel, targetPosition: Vector3) \
         -> double:
      temperature = max(...)
      thermalIrradiance = emissivity * ...  # thermal radiation calculation, Eq. 4
      return thermalIrradiance


class ObservedPanelRadiationModel(PanelRadiationModel):
   """Based on observed fluxes (e.g. from CERES, also requires angular distribution model)"""
   def evaluateIrradianceAtPosition(targetPosition: Vector3):
      observedIrradiance = ...
      return observedIrradiance


################################################################################################
#       TARGETS                                                                                #
################################################################################################

abstract class RadiationPressureTargetModel:
   def evaluateRadiationPressureForce(sourceIrradiance: double,
                                      sourceToTargetDirection: Vector3) -> Vector3:
      """
      Calculate radiation pressure force due to a single source panel onto whole target
      """
      pass


class CannonballRadiationPressureTargetModel(RadiationPressureTargetModel):
   area: double
   coefficient: double

   def evaluateRadiationPressureForce(sourceIrradiance: double,
                                      sourceToTargetDirection: Vector3) -> Vector3:
      force = sourceIrradiance * area * coefficient * ...
      return force


class PaneledRadiationPressureTargetModel(RadiationPressureTargetModel):
   panels: List[TargetPanel]

   def evaluateRadiationPressureForce(sourceIrradiance: double,
                                      sourceToTargetDirection: Vector3) -> Vector3:
      force = Vector3.Zero()
      for panel in panels: # j=1..n
         if not isVisible(panel, sourceToTargetDirection):
            # Panel pointing away from source
            break
         
         reactionDirection = panel.reflectionLaw.evaluateReactionDirection(panel.normal, sourceToTargetDirection)
         force += sourceIrradiance * panel.area * reactionDirection * ...
      return force


class TargetPanel:
   area: double
   normal: Vector3  # body-fixed
   center: Vector3  # body-fixed

   reflectionLaw: ReflectionLaw
