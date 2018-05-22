@prefix jv: <http://vocab.jacksonlabs.com/> .
@prefix jd: <http://data.jacksonlabs.com/> .

@prefix schema: <http://schema.org/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<#list data.pdxInfo as pdx>
<#assign patient_id="${pdx['Patient ID']}">
<#assign _patient="<jd:Patient/${patient_id}>">

${_patient}
	rdf:type jv:Patient ;
	schema:gender <#if "female" == pdx.Gender?lower_case>schema:Female <#else>schema:gender schema:Male</#if> ;
    jv:hasAge "${pdx['Age']}"^^xsd:int ;
    jv:hasInitialDiagnosis "${pdx['Initial Diagnosis']}"^^xsd:string ;
    jv:hasClinicalDiagnosis "${pdx['Clinical Diagnosis']}""^^xsd:string ;
    jv:hasRace "${pdx.Race}"^^xsd:string ;
    jv:hasEthnicity "${pdx.Ethnicity}"^^xsd:string ;
    jv:hasSpecimenSite "${pdx['Specimen Site']}"^^xsd:string ;
    jv:hasTumorType "${pdx['Tumor Type']}"^^xsd:string ;
    jv:hasGrades "${pdx['Grades']}"^^xsd:string ;
    jv:hasTumorStage "${pdx['Tumor Stage']}"^^xsd:string ;
    jv:hasSampleType "${pdx['Sample Type']}"^^xsd:string ;
    jv:hasStrain "${pdx['Strain']}"^^xsd:string ;
    jv:hasMouseSex "${pdx['Mouse Sex']}"^^xsd:string ;
    jv:hasQCStatus "${pdx['QC']}"^^xsd:string ;
    jv:hasEngraftmentSite "${pdx['Engraftment Site']}"^^xsd:string ;
    jv:hasTreatmentNaive "${pdx['Treatment Naive']}"^^xsd:string ;

</#list>
