using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace scheduler_test1
{
    public class ShiftClass
    {
        public ShiftClass()
        {

        }
        private string workerName;
        private string monthName;
        private string dayName;
        private int dayNum;
        private double startHour;
        private double endHour;

        public double getStartHour() { return startHour; }
        public double getEndHour() { return endHour; }
        public string getWorkerName() { return workerName; }
        public string getMonthName() {  return monthName; }
        public string getDayName() { return dayName; }
        public int getDayNum() { return dayNum; }
        public void setStartHour(double hour) { this.startHour = hour; }
        public void setEndHour(double hour) { this.endHour = hour; }
        public void setWorkerName(string name) { this.workerName = name; }
        public void setMonthName(string month) { this.monthName = month; }
        public void setDayName(string day) { this.dayName = day; }
        public void setDayNum(int num) { this.dayNum = num; }
    }
}
