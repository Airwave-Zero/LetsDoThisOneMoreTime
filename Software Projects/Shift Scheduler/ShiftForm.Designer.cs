namespace scheduler_test1
{
    partial class ShiftForm
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
            this.startPanel = new System.Windows.Forms.Panel();
            this.label1 = new System.Windows.Forms.Label();
            this.radio_start5PM = new System.Windows.Forms.RadioButton();
            this.radio_start430PM = new System.Windows.Forms.RadioButton();
            this.radio_start4PM = new System.Windows.Forms.RadioButton();
            this.radio_startCustom = new System.Windows.Forms.RadioButton();
            this.startCustomTextBox = new System.Windows.Forms.TextBox();
            this.radio_start1230PM = new System.Windows.Forms.RadioButton();
            this.radio_start12PM = new System.Windows.Forms.RadioButton();
            this.radio_start1130AM = new System.Windows.Forms.RadioButton();
            this.radio_start11AM = new System.Windows.Forms.RadioButton();
            this.endPanel = new System.Windows.Forms.Panel();
            this.label2 = new System.Windows.Forms.Label();
            this.radio_EndClosing = new System.Windows.Forms.RadioButton();
            this.radio_End1030PM = new System.Windows.Forms.RadioButton();
            this.radio_End10PM = new System.Windows.Forms.RadioButton();
            this.radio_End930PM = new System.Windows.Forms.RadioButton();
            this.radio_End9PM = new System.Windows.Forms.RadioButton();
            this.radio_End830PM = new System.Windows.Forms.RadioButton();
            this.radio_End8PM = new System.Windows.Forms.RadioButton();
            this.radio_EndCustom = new System.Windows.Forms.RadioButton();
            this.endCustomTextBox = new System.Windows.Forms.TextBox();
            this.radio_End430PM = new System.Windows.Forms.RadioButton();
            this.radio_End4PM = new System.Windows.Forms.RadioButton();
            this.radio_End330PM = new System.Windows.Forms.RadioButton();
            this.radio_End3PM = new System.Windows.Forms.RadioButton();
            this.CancelShift_Button = new System.Windows.Forms.Button();
            this.SaveShift_Button = new System.Windows.Forms.Button();
            this.dropdown_WorkerName = new System.Windows.Forms.ComboBox();
            this.WorkerName_Label = new System.Windows.Forms.Label();
            this.checkbox_DeleteShift = new System.Windows.Forms.CheckBox();
            this.ShiftDay_Label = new System.Windows.Forms.Label();
            this.dropdown_ShiftDayName = new System.Windows.Forms.ComboBox();
            this.startPanel.SuspendLayout();
            this.endPanel.SuspendLayout();
            this.SuspendLayout();
            // 
            // startPanel
            // 
            this.startPanel.Controls.Add(this.label1);
            this.startPanel.Controls.Add(this.radio_start5PM);
            this.startPanel.Controls.Add(this.radio_start430PM);
            this.startPanel.Controls.Add(this.radio_start4PM);
            this.startPanel.Controls.Add(this.radio_startCustom);
            this.startPanel.Controls.Add(this.startCustomTextBox);
            this.startPanel.Controls.Add(this.radio_start1230PM);
            this.startPanel.Controls.Add(this.radio_start12PM);
            this.startPanel.Controls.Add(this.radio_start1130AM);
            this.startPanel.Controls.Add(this.radio_start11AM);
            this.startPanel.Location = new System.Drawing.Point(33, 174);
            this.startPanel.Name = "startPanel";
            this.startPanel.Size = new System.Drawing.Size(224, 426);
            this.startPanel.TabIndex = 0;
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Font = new System.Drawing.Font("Microsoft Sans Serif", 16F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.label1.Location = new System.Drawing.Point(57, 9);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(110, 31);
            this.label1.TabIndex = 10;
            this.label1.Text = "Start at:";
            // 
            // radio_start5PM
            // 
            this.radio_start5PM.AutoSize = true;
            this.radio_start5PM.CheckAlign = System.Drawing.ContentAlignment.BottomLeft;
            this.radio_start5PM.Location = new System.Drawing.Point(12, 303);
            this.radio_start5PM.Name = "radio_start5PM";
            this.radio_start5PM.Size = new System.Drawing.Size(58, 20);
            this.radio_start5PM.TabIndex = 8;
            this.radio_start5PM.Text = "5 PM";
            this.radio_start5PM.UseVisualStyleBackColor = true;
            // 
            // radio_start430PM
            // 
            this.radio_start430PM.AutoSize = true;
            this.radio_start430PM.Location = new System.Drawing.Point(12, 263);
            this.radio_start430PM.Name = "radio_start430PM";
            this.radio_start430PM.Size = new System.Drawing.Size(75, 20);
            this.radio_start430PM.TabIndex = 7;
            this.radio_start430PM.Text = "4:30 PM";
            this.radio_start430PM.UseVisualStyleBackColor = true;
            // 
            // radio_start4PM
            // 
            this.radio_start4PM.AutoSize = true;
            this.radio_start4PM.Location = new System.Drawing.Point(12, 223);
            this.radio_start4PM.Name = "radio_start4PM";
            this.radio_start4PM.Size = new System.Drawing.Size(58, 20);
            this.radio_start4PM.TabIndex = 6;
            this.radio_start4PM.Text = "4 PM";
            this.radio_start4PM.UseVisualStyleBackColor = true;
            // 
            // radio_startCustom
            // 
            this.radio_startCustom.AutoSize = true;
            this.radio_startCustom.Location = new System.Drawing.Point(12, 343);
            this.radio_startCustom.Name = "radio_startCustom";
            this.radio_startCustom.Size = new System.Drawing.Size(73, 20);
            this.radio_startCustom.TabIndex = 5;
            this.radio_startCustom.Text = "Custom";
            this.radio_startCustom.UseVisualStyleBackColor = true;
            // 
            // startCustomTextBox
            // 
            this.startCustomTextBox.Enabled = false;
            this.startCustomTextBox.Location = new System.Drawing.Point(12, 375);
            this.startCustomTextBox.Name = "startCustomTextBox";
            this.startCustomTextBox.Size = new System.Drawing.Size(103, 22);
            this.startCustomTextBox.TabIndex = 4;
            // 
            // radio_start1230PM
            // 
            this.radio_start1230PM.AutoSize = true;
            this.radio_start1230PM.Location = new System.Drawing.Point(12, 183);
            this.radio_start1230PM.Name = "radio_start1230PM";
            this.radio_start1230PM.Size = new System.Drawing.Size(82, 20);
            this.radio_start1230PM.TabIndex = 3;
            this.radio_start1230PM.Text = "12:30 PM";
            this.radio_start1230PM.UseVisualStyleBackColor = true;
            // 
            // radio_start12PM
            // 
            this.radio_start12PM.AutoSize = true;
            this.radio_start12PM.CheckAlign = System.Drawing.ContentAlignment.BottomLeft;
            this.radio_start12PM.Location = new System.Drawing.Point(12, 143);
            this.radio_start12PM.Name = "radio_start12PM";
            this.radio_start12PM.Size = new System.Drawing.Size(82, 20);
            this.radio_start12PM.TabIndex = 2;
            this.radio_start12PM.Text = "12:00 PM";
            this.radio_start12PM.UseVisualStyleBackColor = true;
            // 
            // radio_start1130AM
            // 
            this.radio_start1130AM.AutoSize = true;
            this.radio_start1130AM.Location = new System.Drawing.Point(12, 103);
            this.radio_start1130AM.Name = "radio_start1130AM";
            this.radio_start1130AM.Size = new System.Drawing.Size(82, 20);
            this.radio_start1130AM.TabIndex = 1;
            this.radio_start1130AM.Text = "11:30 AM";
            this.radio_start1130AM.UseVisualStyleBackColor = true;
            // 
            // radio_start11AM
            // 
            this.radio_start11AM.AutoSize = true;
            this.radio_start11AM.Checked = true;
            this.radio_start11AM.Location = new System.Drawing.Point(12, 63);
            this.radio_start11AM.Name = "radio_start11AM";
            this.radio_start11AM.Size = new System.Drawing.Size(65, 20);
            this.radio_start11AM.TabIndex = 0;
            this.radio_start11AM.TabStop = true;
            this.radio_start11AM.Text = "11 AM";
            this.radio_start11AM.UseVisualStyleBackColor = true;
            // 
            // endPanel
            // 
            this.endPanel.Controls.Add(this.label2);
            this.endPanel.Controls.Add(this.radio_EndClosing);
            this.endPanel.Controls.Add(this.radio_End1030PM);
            this.endPanel.Controls.Add(this.radio_End10PM);
            this.endPanel.Controls.Add(this.radio_End930PM);
            this.endPanel.Controls.Add(this.radio_End9PM);
            this.endPanel.Controls.Add(this.radio_End830PM);
            this.endPanel.Controls.Add(this.radio_End8PM);
            this.endPanel.Controls.Add(this.radio_EndCustom);
            this.endPanel.Controls.Add(this.endCustomTextBox);
            this.endPanel.Controls.Add(this.radio_End430PM);
            this.endPanel.Controls.Add(this.radio_End4PM);
            this.endPanel.Controls.Add(this.radio_End330PM);
            this.endPanel.Controls.Add(this.radio_End3PM);
            this.endPanel.Location = new System.Drawing.Point(305, 174);
            this.endPanel.Name = "endPanel";
            this.endPanel.Size = new System.Drawing.Size(224, 426);
            this.endPanel.TabIndex = 9;
            // 
            // label2
            // 
            this.label2.AutoSize = true;
            this.label2.Font = new System.Drawing.Font("Microsoft Sans Serif", 16F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.label2.Location = new System.Drawing.Point(69, 9);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(100, 31);
            this.label2.TabIndex = 13;
            this.label2.Text = "End at:";
            // 
            // radio_EndClosing
            // 
            this.radio_EndClosing.AutoSize = true;
            this.radio_EndClosing.Location = new System.Drawing.Point(22, 316);
            this.radio_EndClosing.Name = "radio_EndClosing";
            this.radio_EndClosing.Size = new System.Drawing.Size(73, 20);
            this.radio_EndClosing.TabIndex = 12;
            this.radio_EndClosing.Text = "Closing";
            this.radio_EndClosing.UseVisualStyleBackColor = true;
            // 
            // radio_End1030PM
            // 
            this.radio_End1030PM.AutoSize = true;
            this.radio_End1030PM.Location = new System.Drawing.Point(22, 288);
            this.radio_End1030PM.Name = "radio_End1030PM";
            this.radio_End1030PM.Size = new System.Drawing.Size(82, 20);
            this.radio_End1030PM.TabIndex = 11;
            this.radio_End1030PM.Text = "10:30 PM";
            this.radio_End1030PM.UseVisualStyleBackColor = true;
            // 
            // radio_End10PM
            // 
            this.radio_End10PM.AutoSize = true;
            this.radio_End10PM.Location = new System.Drawing.Point(22, 263);
            this.radio_End10PM.Name = "radio_End10PM";
            this.radio_End10PM.Size = new System.Drawing.Size(65, 20);
            this.radio_End10PM.TabIndex = 10;
            this.radio_End10PM.Text = "10 PM";
            this.radio_End10PM.UseVisualStyleBackColor = true;
            // 
            // radio_End930PM
            // 
            this.radio_End930PM.AutoSize = true;
            this.radio_End930PM.Location = new System.Drawing.Point(22, 238);
            this.radio_End930PM.Name = "radio_End930PM";
            this.radio_End930PM.Size = new System.Drawing.Size(75, 20);
            this.radio_End930PM.TabIndex = 9;
            this.radio_End930PM.Text = "9:30 PM";
            this.radio_End930PM.UseVisualStyleBackColor = true;
            // 
            // radio_End9PM
            // 
            this.radio_End9PM.AutoSize = true;
            this.radio_End9PM.CheckAlign = System.Drawing.ContentAlignment.BottomLeft;
            this.radio_End9PM.Location = new System.Drawing.Point(22, 213);
            this.radio_End9PM.Name = "radio_End9PM";
            this.radio_End9PM.Size = new System.Drawing.Size(58, 20);
            this.radio_End9PM.TabIndex = 8;
            this.radio_End9PM.Text = "9 PM";
            this.radio_End9PM.UseVisualStyleBackColor = true;
            // 
            // radio_End830PM
            // 
            this.radio_End830PM.AutoSize = true;
            this.radio_End830PM.Location = new System.Drawing.Point(22, 188);
            this.radio_End830PM.Name = "radio_End830PM";
            this.radio_End830PM.Size = new System.Drawing.Size(75, 20);
            this.radio_End830PM.TabIndex = 7;
            this.radio_End830PM.Text = "8:30 PM";
            this.radio_End830PM.UseVisualStyleBackColor = true;
            // 
            // radio_End8PM
            // 
            this.radio_End8PM.AutoSize = true;
            this.radio_End8PM.Location = new System.Drawing.Point(22, 163);
            this.radio_End8PM.Name = "radio_End8PM";
            this.radio_End8PM.Size = new System.Drawing.Size(58, 20);
            this.radio_End8PM.TabIndex = 6;
            this.radio_End8PM.Text = "8 PM";
            this.radio_End8PM.UseVisualStyleBackColor = true;
            // 
            // radio_EndCustom
            // 
            this.radio_EndCustom.AutoSize = true;
            this.radio_EndCustom.Location = new System.Drawing.Point(22, 343);
            this.radio_EndCustom.Name = "radio_EndCustom";
            this.radio_EndCustom.Size = new System.Drawing.Size(73, 20);
            this.radio_EndCustom.TabIndex = 5;
            this.radio_EndCustom.Text = "Custom";
            this.radio_EndCustom.UseVisualStyleBackColor = true;
            // 
            // endCustomTextBox
            // 
            this.endCustomTextBox.Enabled = false;
            this.endCustomTextBox.Location = new System.Drawing.Point(22, 375);
            this.endCustomTextBox.Name = "endCustomTextBox";
            this.endCustomTextBox.Size = new System.Drawing.Size(103, 22);
            this.endCustomTextBox.TabIndex = 4;
            // 
            // radio_End430PM
            // 
            this.radio_End430PM.AutoSize = true;
            this.radio_End430PM.Location = new System.Drawing.Point(22, 138);
            this.radio_End430PM.Name = "radio_End430PM";
            this.radio_End430PM.Size = new System.Drawing.Size(75, 20);
            this.radio_End430PM.TabIndex = 3;
            this.radio_End430PM.Text = "4:30 PM";
            this.radio_End430PM.UseVisualStyleBackColor = true;
            // 
            // radio_End4PM
            // 
            this.radio_End4PM.AutoSize = true;
            this.radio_End4PM.CheckAlign = System.Drawing.ContentAlignment.BottomLeft;
            this.radio_End4PM.Location = new System.Drawing.Point(22, 113);
            this.radio_End4PM.Name = "radio_End4PM";
            this.radio_End4PM.Size = new System.Drawing.Size(58, 20);
            this.radio_End4PM.TabIndex = 2;
            this.radio_End4PM.Text = "4 PM";
            this.radio_End4PM.UseVisualStyleBackColor = true;
            // 
            // radio_End330PM
            // 
            this.radio_End330PM.AutoSize = true;
            this.radio_End330PM.Location = new System.Drawing.Point(22, 88);
            this.radio_End330PM.Name = "radio_End330PM";
            this.radio_End330PM.Size = new System.Drawing.Size(75, 20);
            this.radio_End330PM.TabIndex = 1;
            this.radio_End330PM.Text = "3:30 PM";
            this.radio_End330PM.UseVisualStyleBackColor = true;
            // 
            // radio_End3PM
            // 
            this.radio_End3PM.AutoSize = true;
            this.radio_End3PM.Checked = true;
            this.radio_End3PM.Location = new System.Drawing.Point(22, 63);
            this.radio_End3PM.Name = "radio_End3PM";
            this.radio_End3PM.Size = new System.Drawing.Size(58, 20);
            this.radio_End3PM.TabIndex = 0;
            this.radio_End3PM.TabStop = true;
            this.radio_End3PM.Text = "3 PM";
            this.radio_End3PM.UseVisualStyleBackColor = true;
            // 
            // CancelShift_Button
            // 
            this.CancelShift_Button.Location = new System.Drawing.Point(401, 74);
            this.CancelShift_Button.Name = "CancelShift_Button";
            this.CancelShift_Button.Size = new System.Drawing.Size(134, 49);
            this.CancelShift_Button.TabIndex = 10;
            this.CancelShift_Button.Text = "Cancel Changes";
            this.CancelShift_Button.UseVisualStyleBackColor = true;
            this.CancelShift_Button.Click += new System.EventHandler(this.CancelShift_Button_Click);
            // 
            // SaveShift_Button
            // 
            this.SaveShift_Button.Location = new System.Drawing.Point(401, 15);
            this.SaveShift_Button.Name = "SaveShift_Button";
            this.SaveShift_Button.Size = new System.Drawing.Size(134, 49);
            this.SaveShift_Button.TabIndex = 11;
            this.SaveShift_Button.Text = "Save Changes";
            this.SaveShift_Button.UseVisualStyleBackColor = true;
            this.SaveShift_Button.Click += new System.EventHandler(this.SaveShift_Button_Click);
            // 
            // dropdown_WorkerName
            // 
            this.dropdown_WorkerName.FormattingEnabled = true;
            this.dropdown_WorkerName.Location = new System.Drawing.Point(223, 72);
            this.dropdown_WorkerName.Name = "dropdown_WorkerName";
            this.dropdown_WorkerName.Size = new System.Drawing.Size(134, 24);
            this.dropdown_WorkerName.TabIndex = 13;
            this.dropdown_WorkerName.SelectedIndexChanged += new System.EventHandler(this.dropdown_WorkerName_SelectedIndexChanged);
            // 
            // WorkerName_Label
            // 
            this.WorkerName_Label.AutoSize = true;
            this.WorkerName_Label.Font = new System.Drawing.Font("Microsoft Sans Serif", 16F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.WorkerName_Label.Location = new System.Drawing.Point(236, 24);
            this.WorkerName_Label.Name = "WorkerName_Label";
            this.WorkerName_Label.Size = new System.Drawing.Size(109, 31);
            this.WorkerName_Label.TabIndex = 14;
            this.WorkerName_Label.Text = "Worker:";
            // 
            // checkbox_DeleteShift
            // 
            this.checkbox_DeleteShift.AutoSize = true;
            this.checkbox_DeleteShift.Font = new System.Drawing.Font("Microsoft Sans Serif", 12F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.checkbox_DeleteShift.Location = new System.Drawing.Point(401, 133);
            this.checkbox_DeleteShift.Name = "checkbox_DeleteShift";
            this.checkbox_DeleteShift.Size = new System.Drawing.Size(134, 29);
            this.checkbox_DeleteShift.TabIndex = 15;
            this.checkbox_DeleteShift.Text = "Delete Shift";
            this.checkbox_DeleteShift.UseVisualStyleBackColor = true;
            // 
            // ShiftDay_Label
            // 
            this.ShiftDay_Label.AutoSize = true;
            this.ShiftDay_Label.Font = new System.Drawing.Font("Microsoft Sans Serif", 16F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.ShiftDay_Label.Location = new System.Drawing.Point(47, 24);
            this.ShiftDay_Label.Name = "ShiftDay_Label";
            this.ShiftDay_Label.Size = new System.Drawing.Size(133, 31);
            this.ShiftDay_Label.TabIndex = 17;
            this.ShiftDay_Label.Text = "Shift Day:";
            // 
            // dropdown_ShiftDayName
            // 
            this.dropdown_ShiftDayName.FormattingEnabled = true;
            this.dropdown_ShiftDayName.Location = new System.Drawing.Point(46, 72);
            this.dropdown_ShiftDayName.Name = "dropdown_ShiftDayName";
            this.dropdown_ShiftDayName.Size = new System.Drawing.Size(134, 24);
            this.dropdown_ShiftDayName.TabIndex = 16;
            this.dropdown_ShiftDayName.SelectedIndexChanged += new System.EventHandler(this.dropdown_ShiftDayName_SelectedIndexChanged);
            // 
            // ShiftForm
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(8F, 16F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(562, 621);
            this.Controls.Add(this.ShiftDay_Label);
            this.Controls.Add(this.dropdown_ShiftDayName);
            this.Controls.Add(this.checkbox_DeleteShift);
            this.Controls.Add(this.WorkerName_Label);
            this.Controls.Add(this.dropdown_WorkerName);
            this.Controls.Add(this.SaveShift_Button);
            this.Controls.Add(this.CancelShift_Button);
            this.Controls.Add(this.endPanel);
            this.Controls.Add(this.startPanel);
            this.Name = "ShiftForm";
            this.Text = "ShiftForm";
            this.Load += new System.EventHandler(this.ShiftForm_Load);
            this.KeyDown += new System.Windows.Forms.KeyEventHandler(this.ShiftForm_EscapeKeyDown);
            this.startPanel.ResumeLayout(false);
            this.startPanel.PerformLayout();
            this.endPanel.ResumeLayout(false);
            this.endPanel.PerformLayout();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.Panel startPanel;
        private System.Windows.Forms.RadioButton radio_startCustom;
        private System.Windows.Forms.TextBox startCustomTextBox;
        private System.Windows.Forms.RadioButton radio_start1230PM;
        private System.Windows.Forms.RadioButton radio_start12PM;
        private System.Windows.Forms.RadioButton radio_start1130AM;
        private System.Windows.Forms.RadioButton radio_start11AM;
        private System.Windows.Forms.RadioButton radio_start5PM;
        private System.Windows.Forms.RadioButton radio_start430PM;
        private System.Windows.Forms.RadioButton radio_start4PM;
        private System.Windows.Forms.Panel endPanel;
        private System.Windows.Forms.RadioButton radio_End9PM;
        private System.Windows.Forms.RadioButton radio_End830PM;
        private System.Windows.Forms.RadioButton radio_End8PM;
        private System.Windows.Forms.RadioButton radio_EndCustom;
        private System.Windows.Forms.TextBox endCustomTextBox;
        private System.Windows.Forms.RadioButton radio_End430PM;
        private System.Windows.Forms.RadioButton radio_End4PM;
        private System.Windows.Forms.RadioButton radio_End330PM;
        private System.Windows.Forms.RadioButton radio_End3PM;
        private System.Windows.Forms.RadioButton radio_End930PM;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.RadioButton radio_EndClosing;
        private System.Windows.Forms.RadioButton radio_End1030PM;
        private System.Windows.Forms.RadioButton radio_End10PM;
        private System.Windows.Forms.Button CancelShift_Button;
        private System.Windows.Forms.Button SaveShift_Button;
        private System.Windows.Forms.ComboBox dropdown_WorkerName;
        private System.Windows.Forms.Label WorkerName_Label;
        private System.Windows.Forms.CheckBox checkbox_DeleteShift;
        private System.Windows.Forms.Label ShiftDay_Label;
        private System.Windows.Forms.ComboBox dropdown_ShiftDayName;
    }
}