﻿using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace scheduler_test1
{
    public partial class MainUIForm : Form
    {
        public MainUIForm()
        {
            InitializeComponent();
        }

        private void button4_Click(object sender, EventArgs e)
        {

        }

        private void button6_Click(object sender, EventArgs e)
        {
            WorkerForm wForm = new WorkerForm();
            wForm.Show();
        }

        private void button5_Click(object sender, EventArgs e)
        {
            ShiftForm sForm = new ShiftForm();
            sForm.Show();
        }

        private void exportScheduleToolStripMenuItem_Click(object sender, EventArgs e)
        {

        }


        private void Previous_Click(object sender, EventArgs e)
        {

        }


        private void panel2_Paint(object sender, PaintEventArgs e)
        {

        }

    }
}