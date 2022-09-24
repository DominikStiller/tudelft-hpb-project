# HPB Project
This is the repository for the [Honours Programme Bachelor](https://www.tudelft.nl/en/student/faculties/ae-student-portal/education/bachelor/honours-programme/information-for-supervisors) (HPB) project of Dominik Stiller (d.stiller@student.tudelft.nl). The project is supervised by Prof. Dominic Dirkx (d.dirkx@tudelft.nl).

The code for this project can be found in the [feature/radiation_pressure_modeling branch](https://github.com/DominikStiller/tudat/tree/feature/radiation_pressure_modeling) of my Tudat fork.

## Project description
> What is the quantitative influence of using high-accuracy radiation pressure models on the attainable orbit precision for the Lunar Reconaissance Orbiter?

Scientific results obtained from a combination of LRO altimetry, GRAIL gravity field determination and Lunar Laser Ranging can in some cases lead to conflicting results on specific details on lunar geodetic properties (tides, rotation, etc.) Although minor, these discrepancies may not allow the exceptionally accurate data sets that are available to be processed to their inherent accuracy.

For this project, one possible contributor to this issue will be analyzed: errors in non-conservative force modelling of the spacecraft. In particular, this project will investigate the impact of various level of detail of the radiation pressure modelling of the LRO spacecraft, with the aim of contributing to a more robust error budget of the attained orbit determination results.

Sub-objectives:
* Implement high-accuracy (paneled model with/without self-shadowing, albedo, infrared radiation) radiation pressure models
* Validate implemented models
* Analyze influence of choice of model on orbit results
* Analyze influence of choice of model parameters on orbit results
* Analyze influence of ideal initial state estimation on previous two points (optional)

