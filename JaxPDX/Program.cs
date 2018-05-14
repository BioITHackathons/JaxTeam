using System;
using System.Net.Http;
using Newtonsoft.Json;
using System.Threading.Tasks;
using System.Net.Http.Headers;
using Newtonsoft.Json.Linq;
using System.IO;

namespace JaxPDX
{
    class Program
    {
        private static readonly HttpClient client = new HttpClient();
        private static string logPath = "allModelVariances.json";

        static void Main(string[] args)
        {
            ProcessRepositories().Wait();
        }

        private static async Task ProcessRepositories()
        {
            client.DefaultRequestHeaders.Accept.Clear();
            client.DefaultRequestHeaders.Accept.Add(
                new MediaTypeWithQualityHeaderValue("application/json"));

            var stringTask = client.GetStringAsync("http://tumor.informatics.jax.org/PDXInfo/JSONData.do?allModels");
            var varianceUri = "http://tumor.informatics.jax.org/PDXInfo/JSONData.do?modelVariation=";

            var msg = await stringTask;

            JObject obj = JObject.Parse(msg);

            JArray array = new JArray();

            
            foreach (var model in obj["pdxInfo"].Children())
            {
                var modelId = model["Model ID"];

                // use the model ID to get the variance
                var modelVarianceTask = client.GetStringAsync(varianceUri + modelId);

                var modelVariance = await modelVarianceTask;
                JObject variance = JObject.Parse(modelVariance);

                array.Add(variance);
            }

            var logWriter = System.IO.File.CreateText(logPath);

            logWriter.Write(array.ToString());

            logWriter.Flush();
            logWriter = null;
        }
    }
}
