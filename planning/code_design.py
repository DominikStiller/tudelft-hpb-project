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


class RadiationPressureAcceleration(AccelerationModel3d):
   """
   Radiation pressure acceleration from a single source (possibly with multiple source interfaces
   for albedo and thermal) onto a single target.
   """
   source: Body  # e.g. Sun
   target: Body  # e.g. LRO
   occultingBodies: list[Body]  # e.g. Earth and Moon

   def updateMembers(currentTime: double) -> void:
      """"Evaluate radiation pressure acceleration at current time step"""
      force = Vector3.Zero()
      # Iterate over all source panels and their fluxes
      for sourceIrradiance, sourceCenter in source.radiationSourceInterface \
                                             .evaluateAtPosition(target.position): # i=1..m
         sourceToTargetDirection = (target.position - sourceCenter).normalize()
         sourceIrradiance *= calculateShadowFunction(source, occultingBodies, target)
         force += target.evaluateRadiationPressureForce(sourceIrradiance,
                                                         sourceToTargetDirection)
      currentAcceleration = force / target.mass


def calculateShadowFunction(occultedBody: Body, occultingBodies: list[Body], \
                              targetBody: Body) -> double:
   # Calculate using Montenbruck 2000 or Zhang 2019 equations
   # Compared to current function in Tudat, takes multiple occulting bodies


################################################################################################
#       SOURCES                                                                                #
################################################################################################

abstract class RadiationSourceInterface:
   source: Body  # The source that this interface belongs to
                 # For albedo, this is the reflecting body, not the Sun

   def evaluateAtPosition(targetPosition: Vector3) -> list[tuple[double, Vector3]]:
      """
      Calculate irradiance at target position, also return source position. Subclasses
      are aware of source geometry. Return a list of tuples of flux and origin to
      support multiple fluxes with different origins for paneled sources.
      """
      pass


class PointRadiationSourceInterface(RadiationSourceInterface):
   """Point source (for Sun)"""
   radiantPower: double

   def evaluateAtPosition(targetPosition: Vector3) -> list[tuple[double, Vector3]]:
      sourcePosition = source.position
      distanceSourceToTarget = (targetPosition - sourcePosition).norm()
      irradiance = radiantPower / (4 * PI * distanceSourceToTarget**2)  # Eq. 1
      return [(irradiance, sourcePosition)]


class PaneledRadiationSourceInterface(RadiationSourceInterface):
   """Paneled sphere (for planet albedo + thermal radiation)"""
   originalSource: Body  # Usually the Sun, from where incoming radiation originates
   occultingBodies: list[Body]  # For Moon as source, only Earth occults

   panels: list[SourcePanel]
   modelSettings: PaneledRadiationSourceModelSettings  # For example, ALBEDO | THERMAL_KNOCKE

   def _generatePanels():
      # Panelize body and evaluate albedo for panels. For static paneling
      # (independent of spacecraft position), generate once at start of simulation,
      # Query SH albedo model here if available here, or load albedos and
      # emissivities from file
      panels = ...

   def evaluateAtPosition(targetPosition: Vector3) -> list[tuple[double, Vector3]]:
      # For dynamic paneling (depending on target position, spherical cap centered
      # at subsatellite point as in Knocke 1988), could regenerate panels here
      # (possibly with caching), or create separate class
      ret = []
      for panel in panels: # i=1..m
         if not isVisible(panel, targetPosition):
            # Panel hidden at target position
            break

         sourcePosition = source.position + panel.center
         distanceSourceToTarget = (targetPosition - sourcePosition).norm()

         albedoIrradiance = 0
         thermalIrradiance = 0

         if modelSettings & ALBEDO:
            # for received radiation at panel
            shadowFunction = calculateShadowFunction(originalSource, occultingBodies, panel.center)
            albedoIrradiance = \
               shadowFunction * panel.albedo * ...  # albedo radiation calculation, Eq. 2
         if modelSettings & THERMAL_KNOCKE:
            thermalIrradiance = panel.emissivity * ...  # thermal radiation calculation, Eq. 3
         if modelSettings & THERMAL_LEMOINE:
            temperature = max(...)
            thermalIrradiance = panel.emissivity * ...  # thermal radiation calculation, Eq. 4

         ret.append((albedoIrradiance + thermalIrradiance, sourcePosition))
      return ret


class RadiationSourcePanel:
   area: double
   center: Vector3  # Panel center relative to source center
   normal: Vector3

   albedo: Optional[double]
   emissivity: Optional[double]


class PaneledRadiationSourceModelSettings(enum.Flag):
   ALBEDO
   THERMAL_KNOCKE
   THERMAL_LEMOINE


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
