# JaxTeam

Our team is looking at the way forward in terms of the problem of too many ontologies. This tool is also a way to harmonize the diverse databases that we have from a number of research groups.

# Pipeline
This pipeline entails the following steps: <br />
* Data Extraction <br />
* Data Model <br />
* Data Transformation to RDF <br />
* FAIR Evaluation of Tool <br />

# Model
Patient has a Tumor which is a product of some mutation (which has its location in a gene). We want to associate this mutation with a domain. We want to identify the gain or loss of a mutation as it affects the protein domain. The end product is the protein domain.
<br />
Tumor is in a host. Tumor has a passage. 
The original patient has a tumor with about 5 or so fragments and these are planted into the mouse. When its extracted out is
P0.
<br />
Extracted tumor out of the 1st mouse is a passage => P1
<br />Extract tumor from anther mouse P1 and plant in another mouse => P2
<br />
Passage has a mutation which has a genomic location.
<br />
We are looking for mutation in P0 that is lost in P1 or P2.
<br />
Gene model has an ORF which translates into a protein which has a functional protein domain, and this which we are interested in as an end result of our predictions.

