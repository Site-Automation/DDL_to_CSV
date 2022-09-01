import os
import csv

class Point:
    def __init__(self):
        self.type = 'n/a'
        self.system_name = 'n/a'
        self.object_name = 'n/a'
        self.description = 'n/a'
        self.units = 'n/a'
        self.address_hdwr_sys = 'n/a'
        self.n2_trnk_obj = 'n/a'
        self.poll_pri_lpt = 'n/a'
        self.dc_type_lpn_slot_number = 'n/a'
        self.save_point_history = 'n/a'
        self.normal_report_type = 'n/a'
        self.alarm_report_type = 'n/a'
    
    def data_to_list(self):
        data = []
        data.append(self.type)
        data.append(self.system_name)
        data.append(self.object_name)
        data.append(self.description)
        data.append(self.units)
        data.append(self.address_hdwr_sys)
        data.append(self.n2_trnk_obj)
        data.append(self.poll_pri_lpt)
        data.append(self.dc_type_lpn_slot_number)
        data.append(self.save_point_history)
        data.append(self.normal_report_type)
        data.append(self.alarm_report_type)
        return data

    def process_address(self, line_list):
        if self.type == "FPU":
            self.address_hdwr_sys = line_list[1]
            self.n2_trnk_obj = line_list[2]
            self.dc_type_lpn_slot_number = line_list[3]
        else:
            self.address_hdwr_sys = line_list[1]
            self.n2_trnk_obj = line_list[2]
            self.poll_pri_lpt = line_list[3]
            self.dc_type_lpn_slot_number = line_list[4]

    def process_s2direct(self, line_list):
        self.address_hdwr_sys = line_list[1]
        self.n2_trnk_obj = line_list[2]

    def process_hardware(self, line_list):
        self.address_hdwr_sys = line_list[1]
        self.n2_trnk_obj = line_list[2]

    def process_n2openhw(self, line_list):
        self.poll_pri_lpt = line_list[1]
        self.dc_type_lpn_slot_number = line_list[2]

    def process_report(self, line_list):
        if self.type in ["BD", "BI", "BO"]:
            self.save_point_history = line_list[3]
            self.normal_report_type = line_list[6]
            self.alarm_report_type = line_list[7]
        elif self.type in ["AD", "AI", "AO"]:
            self.save_point_history = line_list[3]
            self.normal_report_type = line_list[7]
            self.alarm_report_type = line_list[9]
        elif self.type in ["AOS"]:
            self.save_point_history = line_list[3]

    def process_units(self, line_list):
        if self.type in ["BD", "BI", "BO"]:
            self.units = line_list[1] + ", " + line_list[2]
        elif self.type == "MC":
            units = line_list[1]
            for i in range(2,len(line_list)):
                units += ", " + line_list[i]
            self.units = units
        else:
            if line_list[1] == '':
                self.units = 'n/a'
            else:
                self.units = line_list[1]

    def process_lines(self, line_list):
        for line in line_list:
            line=line.strip().replace('\n','').replace('"','').replace(',','')
            word_list = line.split(" ")
            if word_list[0] == "UNITS":
                self.process_units(word_list)
            elif word_list[0] == "REPORT":
                self.process_report(word_list)
            elif word_list[0] == "ADDRESS":
                self.process_address(word_list)
            elif word_list[0] == "S2DIRECT":
                self.process_s2direct(word_list)
            elif word_list[0] == "HARDWARE":
                self.process_hardware(word_list)
            elif word_list[0] == "N2OPENHW":
                self.process_n2openhw(word_list)
            

def line_is_valid(line):
    if line in ['\n','\r\n','']:
        return False
    elif line[0] == '*':
        return False
    return True

points = []
point_types_to_ignore = ["SLAVE"]

for file_name in os.listdir():
    if file_name.endswith('.DDL'):
        file = open(file_name)
        while True:    
            line = file.readline()
            if line_is_valid(line):
                line_array = line.replace("\n",'').replace('"','').split(',')
                temp = line_array[0].split(' ')
                line_array[0] = temp[0]
                line_array.insert(1, temp[1])                    

                if line_array[0] == "@NC":
                    point=Point()
                    point.type = "NC"
                    point.system_name = line_array[1]
                    point.object_name = line_array[2]
                    points.append(point)
                
                else:
                    if line_array[0] not in point_types_to_ignore:
                        point=Point()
                        point.type = line_array[0]
                        point.system_name = line_array[1]
                        point.object_name = line_array[2]
                        if point.type != "JCB":
                            point.description = line_array[3]
                        line_list = []
                        while True:
                            line = file.readline()
                            if line_is_valid(line):
                                line_list.append(line)
                            else:
                                break
                        point.process_lines(line_list)
                        points.append(point)
                    else:
                        while True:
                            line = file.readline()
                            if not line_is_valid(line):
                                break
            else:
                if not line:
                    break
                continue

        out_file = open(file.name+".csv",'w')
        file.close()
        writer = csv.writer(out_file)
        writer.writerow(["Point Type", "System Name", "Object Name", "Description", "Units", "Address Hdwr Sys", "N2 Trnk Hdwr Obj", "Poll Pri LPT", "DC Type LPN Slot #", "Save Point History", "Normal Report Type", "Alarm Report Type"])
        for point in points:
            writer.writerow(point.data_to_list())
        out_file.close()