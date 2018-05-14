using System;
using System.Net.Http;
using Newtonsoft.Json;
using System.Threading.Tasks;
using System.Net.Http.Headers;
using Newtonsoft.Json.Linq;

namespace JaxPDX
{
    class Program
    {
        private static readonly HttpClient client = new HttpClient();

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
            
            foreach(var model in obj["pdxInfo"].Children())
            {
                var modelId = model["Model ID"];

                // use the model ID to get the variance
                var modelVarianceTask = client.GetStringAsync(varianceUri + modelId);

                var modelVariance = await modelVarianceTask;

                Console.WriteLine(modelVariance);
            }

            Console.ReadKey();
        }
    }
}
