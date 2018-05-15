using Newtonsoft.Json.Linq;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Threading.Tasks;

namespace JaxPDX
{
    class Program
    {
        private static readonly HttpClient client = new HttpClient();

        private static readonly string[] endpointAndJsonFileNames = new string[]{
            "modelVariation",
            "modelHistology",
            "modelCNV",
            "modelExpression"
        };

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
            var baseJsonUri = "http://tumor.informatics.jax.org/PDXInfo/JSONData.do?";

            var msg = await stringTask;

            JObject obj = JObject.Parse(msg);

            JArray[] arrays = new JArray[]{
                new JArray(),
                new JArray(),
                new JArray(),
                new JArray()
            };

            foreach (var model in obj["pdxInfo"].Children())
            {
                var modelId = model["Model ID"];

                for (int ii = 0; ii < arrays.Length; ii++)
                {
                    // use the model ID to get the variance
                    var modelJsonTask = client.GetStringAsync(baseJsonUri + endpointAndJsonFileNames[ii] + "=" + modelId);

                    var modelDetailJson = await modelJsonTask;
                    JObject modelDetail = JObject.Parse(modelDetailJson);

                    arrays[ii].Add(modelDetail);
                }
            }

            for (int jj = 0; jj < endpointAndJsonFileNames.Length; jj++)
            {
                var logWriter = System.IO.File.CreateText(endpointAndJsonFileNames[jj] + ".json");
                
                logWriter.Write(arrays[jj].ToString());

                logWriter.Flush();
                logWriter = null;
            }
        }
    }
}
