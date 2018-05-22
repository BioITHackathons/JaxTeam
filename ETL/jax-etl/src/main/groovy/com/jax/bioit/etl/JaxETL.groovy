package com.jax.bioit.etl

import freemarker.ext.beans.BeansWrapper
import freemarker.ext.beans.BeansWrapperBuilder
import freemarker.template.Configuration
import freemarker.template.Template
import freemarker.template.TemplateHashModel
import groovy.json.JsonSlurper
import groovy.util.logging.Slf4j

@Singleton
@Slf4j
class JaxETL {

    public String process(String templateFileName, def data) {
        /* Create and adjust the configuration singleton */
        Configuration cfg = new Configuration(Configuration.VERSION_2_3_28);
        cfg.setDirectoryForTemplateLoading(new File("."));
        cfg.setDefaultEncoding("UTF-8");


        // Create the builder:
        BeansWrapperBuilder builder = new BeansWrapperBuilder(Configuration.VERSION_2_3_28)
        BeansWrapper wrapper = builder.build()

        TemplateHashModel staticModels = wrapper.getStaticModels()
        TemplateHashModel uuidStatics = (TemplateHashModel) staticModels.get("java.util.UUID")
        TemplateHashModel digestUtilStatics = (TemplateHashModel) staticModels.get("org.apache.commons.codec.digest.DigestUtils")
        TemplateHashModel urlEncoderStatics = (TemplateHashModel) staticModels.get("java.net.URLEncoder")

        /* Create a data-model */
        Map root = new HashMap()
        root.put("uuid", uuidStatics)
        root.put("digestUtil", digestUtilStatics)
        root.put("URLEncoder", urlEncoderStatics)

        /* Get the template (uses cache internally) */
        log.debug("Using template : ${templateFileName}")
        Template temp = cfg.getTemplate(templateFileName)
        root.put("data", data)

        //Writer out = new OutputStreamWriter(new FileOutputStream(new File("test.ttl")), encoder);
        Writer out = new StringWriter()
        temp.process(root, out);

        return out.toString()
    }


    public static void main(String[] args) throws Exception {
        def cli = new CliBuilder(usage:'JaxETL --data <Location of JSON file> --template <Location of Freemarker Template>',
                                 header:'Options:')

        cli.with {
            d longOpt: 'data', args: 1, argName: 'data', 'Full path of the file that contains JSON data'
            t longOpt: 'template', args: 1, argName: 'template', 'Full path of the Freemarker Template used to convert JSON data into RDF'
            o longOpt: 'out', args: 1, argName: 'output', '[Optional] Full path of the output file'
            h  longOpt: 'help', 'Print usage information'
        }

        def options = cli.parse(args)
        if (!options) return

        // Show usage text when -h or --help option is used.
        if (options.h) {
            cli.usage()
            return
        }

        //Mandatory options
        assert(options.d)
        assert(options.t)

//        println "${new File(".").getAbsolutePath()}"
//        def jsonFile = new File("jax_AllModels.json")
//        JsonSlurper jsonSlurper = new JsonSlurper()
//        def jsonData = jsonFile.text
//        println jsonData
//        def data = jsonSlurper.parseText(jsonData)
//        def model = JaxETL.instance.process("jax_patient.ftl", data)

        def jsonFile = new File(options.d)

        JsonSlurper jsonSlurper = new JsonSlurper()
        def jsonData = jsonFile.text

        //println jsonData

        def data = jsonSlurper.parseText(jsonData)
        def model = JaxETL.instance.process(options.t, data)

        if (options.o) {
            def rdfFile = new File('jax_patients.ttl')
            rdfFile.write(model)
        } else {
            log.debug (model)
            println model
        }
    }
}
