﻿using System.Drawing;
using System.Windows.Forms;

namespace scheduler_test1
{
    partial class MainUIForm
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            this.Workers_Button = new System.Windows.Forms.Button();
            this.button4 = new System.Windows.Forms.Button();
            this.panel1 = new System.Windows.Forms.Panel();
            this.Add_Shift = new System.Windows.Forms.Button();
            this.Next = new System.Windows.Forms.Button();
            this.Previous = new System.Windows.Forms.Button();
            this.richTextBox1 = new System.Windows.Forms.RichTextBox();
            this.panel2 = new System.Windows.Forms.Panel();
            this.panel10 = new System.Windows.Forms.Panel();
            this.panel9 = new System.Windows.Forms.Panel();
            this.panel11 = new System.Windows.Forms.Panel();
            this.panel8 = new System.Windows.Forms.Panel();
            this.panel12 = new System.Windows.Forms.Panel();
            this.panel7 = new System.Windows.Forms.Panel();
            this.panel13 = new System.Windows.Forms.Panel();
            this.panel6 = new System.Windows.Forms.Panel();
            this.panel14 = new System.Windows.Forms.Panel();
            this.panel5 = new System.Windows.Forms.Panel();
            this.panel15 = new System.Windows.Forms.Panel();
            this.panel4 = new System.Windows.Forms.Panel();
            this.panel16 = new System.Windows.Forms.Panel();
            this.panel3 = new System.Windows.Forms.Panel();
            this.fileToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.importScheduleToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.exportScheduleAsJSONToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.exportScheduleAsPNGStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.saveScheduleToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.workersToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.addEditRulesToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.addViewDaysOffToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.importWorkersToolStripMenuItem1 = new System.Windows.Forms.ToolStripMenuItem();
            this.exportWorkersToolStripMenuItem1 = new System.Windows.Forms.ToolStripMenuItem();
            this.menuStrip1 = new System.Windows.Forms.MenuStrip();
            this.SundayTextBox = new System.Windows.Forms.TextBox();
            this.MondayTextBox = new System.Windows.Forms.TextBox();
            this.TuesdayTextBox = new System.Windows.Forms.TextBox();
            this.WednesdayTextBox = new System.Windows.Forms.TextBox();
            this.ThursdayTextBox = new System.Windows.Forms.TextBox();
            this.FridayTextBox = new System.Windows.Forms.TextBox();
            this.SaturdayTextBox = new System.Windows.Forms.TextBox();
            this.DuplicateShiftButton = new System.Windows.Forms.Button();
            this.panel1.SuspendLayout();
            this.panel2.SuspendLayout();
            this.menuStrip1.SuspendLayout();
            this.SuspendLayout();
            // 
            // Workers_Button
            // 
            this.Workers_Button.Location = new System.Drawing.Point(847, 5);
            this.Workers_Button.Name = "Workers_Button";
            this.Workers_Button.Size = new System.Drawing.Size(107, 24);
            this.Workers_Button.TabIndex = 7;
            this.Workers_Button.Text = "WORKERS";
            this.Workers_Button.UseVisualStyleBackColor = true;
            this.Workers_Button.Click += new System.EventHandler(this.WorkerForm_Click);
            // 
            // button4
            // 
            this.button4.Location = new System.Drawing.Point(1004, 5);
            this.button4.Name = "button4";
            this.button4.Size = new System.Drawing.Size(188, 24);
            this.button4.TabIndex = 5;
            this.button4.Text = "GENERATE SCHEDULE";
            this.button4.UseVisualStyleBackColor = true;
            this.button4.Click += new System.EventHandler(this.GenerateSchedule_Click);
            // 
            // panel1
            // 
            this.panel1.Controls.Add(this.DuplicateShiftButton);
            this.panel1.Controls.Add(this.Add_Shift);
            this.panel1.Controls.Add(this.Next);
            this.panel1.Controls.Add(this.Previous);
            this.panel1.Controls.Add(this.richTextBox1);
            this.panel1.Controls.Add(this.button4);
            this.panel1.Controls.Add(this.Workers_Button);
            this.panel1.Location = new System.Drawing.Point(12, 31);
            this.panel1.Name = "panel1";
            this.panel1.Size = new System.Drawing.Size(1207, 42);
            this.panel1.TabIndex = 9;
            // 
            // Add_Shift
            // 
            this.Add_Shift.Location = new System.Drawing.Point(77, 5);
            this.Add_Shift.Name = "Add_Shift";
            this.Add_Shift.Size = new System.Drawing.Size(125, 24);
            this.Add_Shift.TabIndex = 10;
            this.Add_Shift.Text = "ADD SHIFT";
            this.Add_Shift.UseVisualStyleBackColor = true;
            this.Add_Shift.Click += new System.EventHandler(this.Add_Shift_Click);
            // 
            // Next
            // 
            this.Next.Font = new System.Drawing.Font("Microsoft Sans Serif", 10F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.Next.Location = new System.Drawing.Point(770, 4);
            this.Next.Name = "Next";
            this.Next.Size = new System.Drawing.Size(27, 27);
            this.Next.TabIndex = 0;
            this.Next.Text = "▶";
            this.Next.UseVisualStyleBackColor = true;
            // 
            // Previous
            // 
            this.Previous.Font = new System.Drawing.Font("Microsoft Sans Serif", 10F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.Previous.Location = new System.Drawing.Point(433, 4);
            this.Previous.Name = "Previous";
            this.Previous.Size = new System.Drawing.Size(27, 27);
            this.Previous.TabIndex = 9;
            this.Previous.Text = "◀";
            this.Previous.UseVisualStyleBackColor = true;
            this.Previous.Click += new System.EventHandler(this.Previous_Click);
            // 
            // richTextBox1
            // 
            this.richTextBox1.Font = new System.Drawing.Font("Microsoft Sans Serif", 12F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.richTextBox1.Location = new System.Drawing.Point(479, 4);
            this.richTextBox1.Name = "richTextBox1";
            this.richTextBox1.ReadOnly = true;
            this.richTextBox1.ScrollBars = System.Windows.Forms.RichTextBoxScrollBars.None;
            this.richTextBox1.Size = new System.Drawing.Size(273, 27);
            this.richTextBox1.TabIndex = 8;
            this.richTextBox1.Text = "Month D1-D7 Year";
            // 
            // panel2
            // 
            this.panel2.Controls.Add(this.panel10);
            this.panel2.Controls.Add(this.panel9);
            this.panel2.Controls.Add(this.panel11);
            this.panel2.Controls.Add(this.panel8);
            this.panel2.Controls.Add(this.panel12);
            this.panel2.Controls.Add(this.panel7);
            this.panel2.Controls.Add(this.panel13);
            this.panel2.Controls.Add(this.panel6);
            this.panel2.Controls.Add(this.panel14);
            this.panel2.Controls.Add(this.panel5);
            this.panel2.Controls.Add(this.panel15);
            this.panel2.Controls.Add(this.panel4);
            this.panel2.Controls.Add(this.panel16);
            this.panel2.Controls.Add(this.panel3);
            this.panel2.Location = new System.Drawing.Point(12, 114);
            this.panel2.Name = "panel2";
            this.panel2.Size = new System.Drawing.Size(1207, 645);
            this.panel2.TabIndex = 10;
            // 
            // panel10
            // 
            this.panel10.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.panel10.Location = new System.Drawing.Point(1044, 265);
            this.panel10.Name = "panel10";
            this.panel10.Size = new System.Drawing.Size(152, 377);
            this.panel10.TabIndex = 3;
            // 
            // panel9
            // 
            this.panel9.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.panel9.Location = new System.Drawing.Point(1044, 3);
            this.panel9.Name = "panel9";
            this.panel9.Size = new System.Drawing.Size(152, 256);
            this.panel9.TabIndex = 1;
            // 
            // panel11
            // 
            this.panel11.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.panel11.Location = new System.Drawing.Point(871, 265);
            this.panel11.Name = "panel11";
            this.panel11.Size = new System.Drawing.Size(152, 377);
            this.panel11.TabIndex = 4;
            // 
            // panel8
            // 
            this.panel8.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.panel8.Location = new System.Drawing.Point(871, 3);
            this.panel8.Name = "panel8";
            this.panel8.Size = new System.Drawing.Size(152, 256);
            this.panel8.TabIndex = 1;
            // 
            // panel12
            // 
            this.panel12.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.panel12.Location = new System.Drawing.Point(698, 265);
            this.panel12.Name = "panel12";
            this.panel12.Size = new System.Drawing.Size(152, 377);
            this.panel12.TabIndex = 5;
            // 
            // panel7
            // 
            this.panel7.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.panel7.Location = new System.Drawing.Point(698, 3);
            this.panel7.Name = "panel7";
            this.panel7.Size = new System.Drawing.Size(152, 256);
            this.panel7.TabIndex = 1;
            // 
            // panel13
            // 
            this.panel13.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.panel13.Location = new System.Drawing.Point(525, 265);
            this.panel13.Name = "panel13";
            this.panel13.Size = new System.Drawing.Size(152, 377);
            this.panel13.TabIndex = 6;
            // 
            // panel6
            // 
            this.panel6.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.panel6.Location = new System.Drawing.Point(525, 3);
            this.panel6.Name = "panel6";
            this.panel6.Size = new System.Drawing.Size(152, 256);
            this.panel6.TabIndex = 1;
            // 
            // panel14
            // 
            this.panel14.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.panel14.Location = new System.Drawing.Point(352, 265);
            this.panel14.Name = "panel14";
            this.panel14.Size = new System.Drawing.Size(152, 377);
            this.panel14.TabIndex = 7;
            // 
            // panel5
            // 
            this.panel5.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.panel5.Location = new System.Drawing.Point(352, 3);
            this.panel5.Name = "panel5";
            this.panel5.Size = new System.Drawing.Size(152, 256);
            this.panel5.TabIndex = 1;
            // 
            // panel15
            // 
            this.panel15.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.panel15.Location = new System.Drawing.Point(179, 265);
            this.panel15.Name = "panel15";
            this.panel15.Size = new System.Drawing.Size(152, 377);
            this.panel15.TabIndex = 8;
            // 
            // panel4
            // 
            this.panel4.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.panel4.Location = new System.Drawing.Point(179, 3);
            this.panel4.Name = "panel4";
            this.panel4.Size = new System.Drawing.Size(152, 256);
            this.panel4.TabIndex = 1;
            // 
            // panel16
            // 
            this.panel16.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.panel16.Location = new System.Drawing.Point(6, 265);
            this.panel16.Name = "panel16";
            this.panel16.Size = new System.Drawing.Size(152, 377);
            this.panel16.TabIndex = 2;
            // 
            // panel3
            // 
            this.panel3.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.panel3.Location = new System.Drawing.Point(6, 3);
            this.panel3.Name = "panel3";
            this.panel3.Size = new System.Drawing.Size(152, 256);
            this.panel3.TabIndex = 0;
            // 
            // fileToolStripMenuItem
            // 
            this.fileToolStripMenuItem.DropDownItems.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.importScheduleToolStripMenuItem,
            this.exportScheduleAsJSONToolStripMenuItem,
            this.exportScheduleAsPNGStripMenuItem,
            this.saveScheduleToolStripMenuItem});
            this.fileToolStripMenuItem.Name = "fileToolStripMenuItem";
            this.fileToolStripMenuItem.Size = new System.Drawing.Size(46, 24);
            this.fileToolStripMenuItem.Text = "File";
            // 
            // importScheduleToolStripMenuItem
            // 
            this.importScheduleToolStripMenuItem.Name = "importScheduleToolStripMenuItem";
            this.importScheduleToolStripMenuItem.Size = new System.Drawing.Size(256, 26);
            this.importScheduleToolStripMenuItem.Text = "Import Schedule";
            this.importScheduleToolStripMenuItem.Click += new System.EventHandler(this.importScheduleToolStripMenuItem_Click);
            // 
            // exportScheduleAsJSONToolStripMenuItem
            // 
            this.exportScheduleAsJSONToolStripMenuItem.Name = "exportScheduleAsJSONToolStripMenuItem";
            this.exportScheduleAsJSONToolStripMenuItem.Size = new System.Drawing.Size(256, 26);
            this.exportScheduleAsJSONToolStripMenuItem.Text = "Export Schedule as JSON";
            this.exportScheduleAsJSONToolStripMenuItem.Click += new System.EventHandler(this.exportScheduleJSONToolStripMenuItem_Click);
            // 
            // exportScheduleAsPNGStripMenuItem
            // 
            this.exportScheduleAsPNGStripMenuItem.Name = "exportScheduleAsPNGStripMenuItem";
            this.exportScheduleAsPNGStripMenuItem.Size = new System.Drawing.Size(256, 26);
            this.exportScheduleAsPNGStripMenuItem.Text = "Export Schedule as PNG";
            this.exportScheduleAsPNGStripMenuItem.Click += new System.EventHandler(this.exportSchedulePNGToolStripMenuItem_Click);
            // 
            // saveScheduleToolStripMenuItem
            // 
            this.saveScheduleToolStripMenuItem.Name = "saveScheduleToolStripMenuItem";
            this.saveScheduleToolStripMenuItem.ShortcutKeys = ((System.Windows.Forms.Keys)((System.Windows.Forms.Keys.Control | System.Windows.Forms.Keys.S)));
            this.saveScheduleToolStripMenuItem.Size = new System.Drawing.Size(256, 26);
            this.saveScheduleToolStripMenuItem.Text = "Save Schedule";
            // 
            // workersToolStripMenuItem
            // 
            this.workersToolStripMenuItem.DropDownItems.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.addEditRulesToolStripMenuItem,
            this.addViewDaysOffToolStripMenuItem,
            this.importWorkersToolStripMenuItem1,
            this.exportWorkersToolStripMenuItem1});
            this.workersToolStripMenuItem.Name = "workersToolStripMenuItem";
            this.workersToolStripMenuItem.Size = new System.Drawing.Size(76, 24);
            this.workersToolStripMenuItem.Text = "Workers";
            // 
            // addEditRulesToolStripMenuItem
            // 
            this.addEditRulesToolStripMenuItem.Name = "addEditRulesToolStripMenuItem";
            this.addEditRulesToolStripMenuItem.Size = new System.Drawing.Size(224, 26);
            this.addEditRulesToolStripMenuItem.Text = "Add/Edit Rules";
            // 
            // addViewDaysOffToolStripMenuItem
            // 
            this.addViewDaysOffToolStripMenuItem.Name = "addViewDaysOffToolStripMenuItem";
            this.addViewDaysOffToolStripMenuItem.Size = new System.Drawing.Size(224, 26);
            this.addViewDaysOffToolStripMenuItem.Text = "Add/View Days Off";
            // 
            // importWorkersToolStripMenuItem1
            // 
            this.importWorkersToolStripMenuItem1.Name = "importWorkersToolStripMenuItem1";
            this.importWorkersToolStripMenuItem1.Size = new System.Drawing.Size(224, 26);
            this.importWorkersToolStripMenuItem1.Text = "Import Workers";
            this.importWorkersToolStripMenuItem1.Click += new System.EventHandler(this.importWorkersToolStripMenuItem1_Click);
            // 
            // exportWorkersToolStripMenuItem1
            // 
            this.exportWorkersToolStripMenuItem1.Name = "exportWorkersToolStripMenuItem1";
            this.exportWorkersToolStripMenuItem1.Size = new System.Drawing.Size(224, 26);
            this.exportWorkersToolStripMenuItem1.Text = "Export Workers";
            this.exportWorkersToolStripMenuItem1.Click += new System.EventHandler(this.exportWorkersToolStripMenuItem1_Click);
            // 
            // menuStrip1
            // 
            this.menuStrip1.ImageScalingSize = new System.Drawing.Size(20, 20);
            this.menuStrip1.Items.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.fileToolStripMenuItem,
            this.workersToolStripMenuItem});
            this.menuStrip1.Location = new System.Drawing.Point(0, 0);
            this.menuStrip1.Name = "menuStrip1";
            this.menuStrip1.Size = new System.Drawing.Size(1229, 28);
            this.menuStrip1.TabIndex = 8;
            this.menuStrip1.Text = "menuStrip1";
            // 
            // SundayTextBox
            // 
            this.SundayTextBox.BackColor = this.BackColor;
            this.SundayTextBox.BorderStyle = System.Windows.Forms.BorderStyle.None;
            this.SundayTextBox.Font = new System.Drawing.Font("Microsoft Sans Serif", 12F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.SundayTextBox.Location = new System.Drawing.Point(1058, 83);
            this.SundayTextBox.Name = "SundayTextBox";
            this.SundayTextBox.ReadOnly = true;
            this.SundayTextBox.Size = new System.Drawing.Size(152, 23);
            this.SundayTextBox.TabIndex = 11;
            this.SundayTextBox.Text = "Sunday";
            this.SundayTextBox.TextAlign = System.Windows.Forms.HorizontalAlignment.Center;
            // 
            // MondayTextBox
            // 
            this.MondayTextBox.BackColor = this.BackColor;
            this.MondayTextBox.BorderStyle = System.Windows.Forms.BorderStyle.None;
            this.MondayTextBox.Font = new System.Drawing.Font("Microsoft Sans Serif", 12F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.MondayTextBox.Location = new System.Drawing.Point(20, 83);
            this.MondayTextBox.Name = "MondayTextBox";
            this.MondayTextBox.ReadOnly = true;
            this.MondayTextBox.Size = new System.Drawing.Size(152, 23);
            this.MondayTextBox.TabIndex = 12;
            this.MondayTextBox.Text = "Monday";
            this.MondayTextBox.TextAlign = System.Windows.Forms.HorizontalAlignment.Center;
            // 
            // TuesdayTextBox
            // 
            this.TuesdayTextBox.BackColor = this.BackColor;
            this.TuesdayTextBox.BorderStyle = System.Windows.Forms.BorderStyle.None;
            this.TuesdayTextBox.Font = new System.Drawing.Font("Microsoft Sans Serif", 12F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.TuesdayTextBox.Location = new System.Drawing.Point(193, 83);
            this.TuesdayTextBox.Name = "TuesdayTextBox";
            this.TuesdayTextBox.ReadOnly = true;
            this.TuesdayTextBox.Size = new System.Drawing.Size(152, 23);
            this.TuesdayTextBox.TabIndex = 13;
            this.TuesdayTextBox.Text = "Tuesday";
            this.TuesdayTextBox.TextAlign = System.Windows.Forms.HorizontalAlignment.Center;
            // 
            // WednesdayTextBox
            // 
            this.WednesdayTextBox.BackColor = this.BackColor;
            this.WednesdayTextBox.BorderStyle = System.Windows.Forms.BorderStyle.None;
            this.WednesdayTextBox.Font = new System.Drawing.Font("Microsoft Sans Serif", 12F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.WednesdayTextBox.Location = new System.Drawing.Point(366, 83);
            this.WednesdayTextBox.Name = "WednesdayTextBox";
            this.WednesdayTextBox.ReadOnly = true;
            this.WednesdayTextBox.Size = new System.Drawing.Size(152, 23);
            this.WednesdayTextBox.TabIndex = 14;
            this.WednesdayTextBox.Text = "Wednesday";
            this.WednesdayTextBox.TextAlign = System.Windows.Forms.HorizontalAlignment.Center;
            // 
            // ThursdayTextBox
            // 
            this.ThursdayTextBox.BackColor = this.BackColor;
            this.ThursdayTextBox.BorderStyle = System.Windows.Forms.BorderStyle.None;
            this.ThursdayTextBox.Font = new System.Drawing.Font("Microsoft Sans Serif", 12F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.ThursdayTextBox.Location = new System.Drawing.Point(539, 83);
            this.ThursdayTextBox.Name = "ThursdayTextBox";
            this.ThursdayTextBox.ReadOnly = true;
            this.ThursdayTextBox.Size = new System.Drawing.Size(152, 23);
            this.ThursdayTextBox.TabIndex = 15;
            this.ThursdayTextBox.Text = "Thursday";
            this.ThursdayTextBox.TextAlign = System.Windows.Forms.HorizontalAlignment.Center;
            // 
            // FridayTextBox
            // 
            this.FridayTextBox.BackColor = this.BackColor;
            this.FridayTextBox.BorderStyle = System.Windows.Forms.BorderStyle.None;
            this.FridayTextBox.Font = new System.Drawing.Font("Microsoft Sans Serif", 12F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.FridayTextBox.Location = new System.Drawing.Point(712, 83);
            this.FridayTextBox.Name = "FridayTextBox";
            this.FridayTextBox.ReadOnly = true;
            this.FridayTextBox.Size = new System.Drawing.Size(152, 23);
            this.FridayTextBox.TabIndex = 16;
            this.FridayTextBox.Text = "Friday";
            this.FridayTextBox.TextAlign = System.Windows.Forms.HorizontalAlignment.Center;
            // 
            // SaturdayTextBox
            // 
            this.SaturdayTextBox.BackColor = this.BackColor;
            this.SaturdayTextBox.BorderStyle = System.Windows.Forms.BorderStyle.None;
            this.SaturdayTextBox.Font = new System.Drawing.Font("Microsoft Sans Serif", 12F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.SaturdayTextBox.Location = new System.Drawing.Point(885, 83);
            this.SaturdayTextBox.Name = "SaturdayTextBox";
            this.SaturdayTextBox.ReadOnly = true;
            this.SaturdayTextBox.Size = new System.Drawing.Size(152, 23);
            this.SaturdayTextBox.TabIndex = 17;
            this.SaturdayTextBox.Text = "Saturday";
            this.SaturdayTextBox.TextAlign = System.Windows.Forms.HorizontalAlignment.Center;
            // 
            // DuplicateShiftButton
            // 
            this.DuplicateShiftButton.Enabled = false;
            this.DuplicateShiftButton.Location = new System.Drawing.Point(253, 5);
            this.DuplicateShiftButton.Name = "DuplicateShiftButton";
            this.DuplicateShiftButton.Size = new System.Drawing.Size(141, 24);
            this.DuplicateShiftButton.TabIndex = 11;
            this.DuplicateShiftButton.Text = "DUPLICATE SHIFT";
            this.DuplicateShiftButton.UseVisualStyleBackColor = true;
            // 
            // MainUIForm
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(8F, 16F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(1229, 778);
            this.Controls.Add(this.SaturdayTextBox);
            this.Controls.Add(this.FridayTextBox);
            this.Controls.Add(this.ThursdayTextBox);
            this.Controls.Add(this.WednesdayTextBox);
            this.Controls.Add(this.TuesdayTextBox);
            this.Controls.Add(this.MondayTextBox);
            this.Controls.Add(this.SundayTextBox);
            this.Controls.Add(this.panel1);
            this.Controls.Add(this.panel2);
            this.Controls.Add(this.menuStrip1);
            this.MainMenuStrip = this.menuStrip1;
            this.Name = "MainUIForm";
            this.Text = "Dpot Scheduler v1.0";
            this.Load += new System.EventHandler(this.MainUIForm_Load);
            this.panel1.ResumeLayout(false);
            this.panel2.ResumeLayout(false);
            this.menuStrip1.ResumeLayout(false);
            this.menuStrip1.PerformLayout();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion
        private System.Windows.Forms.Button Workers_Button;
        private System.Windows.Forms.Button button4;
        private System.Windows.Forms.Panel panel1;
        private System.Windows.Forms.Panel panel2;
        private System.Windows.Forms.ToolStripMenuItem fileToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem importScheduleToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem exportScheduleAsJSONToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem exportScheduleAsPNGStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem saveScheduleToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem workersToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem addEditRulesToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem addViewDaysOffToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem importWorkersToolStripMenuItem1;
        private System.Windows.Forms.ToolStripMenuItem exportWorkersToolStripMenuItem1;
        private System.Windows.Forms.MenuStrip menuStrip1;
        private System.Windows.Forms.RichTextBox richTextBox1;
        private System.Windows.Forms.Button Previous;
        private System.Windows.Forms.Button Next;
        private System.Windows.Forms.TextBox SundayTextBox;
        private System.Windows.Forms.TextBox MondayTextBox;
        private System.Windows.Forms.TextBox TuesdayTextBox;
        private System.Windows.Forms.TextBox WednesdayTextBox;
        private System.Windows.Forms.TextBox ThursdayTextBox;
        private System.Windows.Forms.TextBox FridayTextBox;
        private System.Windows.Forms.TextBox SaturdayTextBox;
        private Panel panel3;
        private Panel panel9;
        private Panel panel8;
        private Panel panel7;
        private Panel panel6;
        private Panel panel5;
        private Panel panel4;
        private Panel panel10;
        private Panel panel11;
        private Panel panel12;
        private Panel panel13;
        private Panel panel14;
        private Panel panel15;
        private Panel panel16;
        private Button Add_Shift;
        private Button DuplicateShiftButton;
    }
}

