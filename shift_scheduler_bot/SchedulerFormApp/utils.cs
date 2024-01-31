using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using static System.Windows.Forms.VisualStyles.VisualStyleElement.Window;

namespace scheduler_test1
{
    public static class Utils
    {
        public static string exportJSONFile(string data)
        /*
         * Simple re-usable function that prompts user to select a file location to save the
         * raw string data into and then saves it there.
         * TODO: figure out a way to reuse code for import/export since the only difference 
         * is really just what type of object to initialize at the start? There's gotta
         * be some way, unless the inherent strong typing of C# makes this undoable
         */
        // TODO: add checking/guardrail if user imports wrong file
        {
            Stream myStream;
            SaveFileDialog saveFileDialog1 = new SaveFileDialog();
            string fileName = "";

            saveFileDialog1.Filter = "JSON files (*.JSON)|*.JSON|All files (*.*)|*.*";
            saveFileDialog1.FilterIndex = 2;
            saveFileDialog1.RestoreDirectory = true;

            if (saveFileDialog1.ShowDialog() == DialogResult.OK)
            {
                if ((myStream = saveFileDialog1.OpenFile()) != null)
                {
                    //filename is saveFileDialog1.FileName
                    System.IO.File.WriteAllText(saveFileDialog1.FileName, data);
                    fileName = saveFileDialog1.FileName;
                    myStream.Close();
                    myStream.Dispose();
                }
            }
            return fileName;
        }
        public static string importJSONFile()
        /*
         * Simple re-usable function that prompts user to select a JSON and returns
         * the file name of the file selected, empty string if none selected
         */
        // TODO: add checking/guardrail if user imports wrong file
        {
            Stream myStream;
            OpenFileDialog openFileDialog1 = new OpenFileDialog();
            string fileName = "";

            openFileDialog1.Filter = "JSON files (*.JSON)|*.JSON|All files (*.*)|*.*";
            openFileDialog1.FilterIndex = 2;
            openFileDialog1.RestoreDirectory = true;

            if (openFileDialog1.ShowDialog() == DialogResult.OK)
            {
                if ((myStream = openFileDialog1.OpenFile()) != null)
                {

                    //filename is saveFileDialog1.FileName
                    fileName = openFileDialog1.FileName;
                    myStream.Close();
                    myStream.Dispose();
                }
            }
            return fileName;
        }
    }
}
