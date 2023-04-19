class Sheetmetal_buildCosting_cal:
    def sheet_mesh(self, sheet_size, mesh_size):
        sheets_size = []
        x_size = sheet_size[0]/mesh_size
        y_size = sheet_size[1]/mesh_size
        for i in range(0, int(round(((sheet_size[0])/mesh_size), 0))):
            for j in range(0, int(round(((sheet_size[1])/mesh_size), 0))):
                x = mesh_size + (j * mesh_size)
                y = mesh_size + (i * mesh_size)
                sheets_size.append([x, y])
        return sheets_size
    def check_size(self, blank_size, sheet_size):
        if max(blank_size) < max(sheet_size) and min(blank_size) < min(sheet_size):
            return "Cool"
        else:
            return "Blank Size is Too Large"
    def check_qty(self, blank_size, ver_sheet_size):
        max_max = max(ver_sheet_size)//max(blank_size)
        min_min = min(ver_sheet_size)//min(blank_size)
        type_1 = int(max_max) * int(min_min)
        max_min = max(ver_sheet_size)//min(blank_size)
        min_max = min(ver_sheet_size)//max(blank_size)
        type_2 = int(max_min) * int(min_max)
        if type_1 > type_2:
            return type_1
        else:
            return type_2
    def full_sheet_qty(self, blank_size, sheet_size):
        cal_nos = self.check_qty(blank_size, sheet_size)
        return cal_nos
    def nesting_sheet_size(self, blank_size, sheet_size, nos, mesh_size=312.5):
        data_ = self.check_size(blank_size, sheet_size)
        sheets_size = self.sheet_mesh(sheet_size, mesh_size)
        if data_ == "Cool" and nos == 1:
            for i in range(len(sheets_size)):
                sheets_size[i].sort()
                if blank_size[0] <= sheets_size[i][0] and blank_size[1] <= sheets_size[i][1]:
                    optimum_qty = self.check_qty(blank_size, sheets_size[i])
                    return 0, nos, sheets_size[i], 0, optimum_qty
        elif data_ == "Cool" and self.full_sheet_qty(blank_size, sheet_size) <= nos:
            no_of_sheet = nos // self.full_sheet_qty(blank_size, sheet_size)
            remaining_qty = nos - \
                self.full_sheet_qty(blank_size, sheet_size)*no_of_sheet
            for i in range(len(sheets_size)):
                sheets_size[i].sort()
                cal_nos = self.check_qty(blank_size, sheets_size[i])
                if cal_nos >= remaining_qty and remaining_qty != 0:
                    optimum_qty = cal_nos + no_of_sheet * \
                        self.full_sheet_qty(blank_size, sheet_size)
                    return no_of_sheet, nos, sheets_size[i], remaining_qty, optimum_qty
                elif remaining_qty == 0:
                    optimum_qty = nos
                    return no_of_sheet, nos, [0, 0], remaining_qty, optimum_qty
        elif data_ == "Cool" and self.full_sheet_qty(blank_size, sheet_size) > nos:
            for i in range(len(sheets_size)):
                sheets_size[i].sort()
                cal_nos = self.check_qty(blank_size, sheets_size[i])
                if cal_nos >= nos:
                    optimum_qty = cal_nos
                    return 0, nos, sheets_size[i], 0, optimum_qty
        else:
            return data_
    def get_total_volume(self, sheet_nest_data, sheet_size, thk):
        volume = ((sheet_nest_data[0] * sheet_size[0] * sheet_size[1]) +
                  (sheet_nest_data[2][0] * sheet_nest_data[2][1])) * thk
        return round(volume / 1000, 3)
    def get_total_wt(self, volum, density):
        wt_total = volum * density / 1000
        return round(wt_total, 3)
    def get_wt(self, wt, nos):
        wt_per_part = wt/nos
        return round(wt_per_part, 3)
    def get_rm_cost(self, wt_per_part, rm_rate):
        rm_cost = wt_per_part * rm_rate
        return round(rm_cost, 2)
    def get_cutting_cost(self, c_mf, perimeter, thk, no_of_start, ns_mf):
        cutting_cost = (perimeter * c_mf * thk) + (no_of_start * ns_mf)
        return round(cutting_cost, 2)
    def optimun_rm_cost(self, wt, sheet_nest_data, rm_rate):
        opt_rm_cost = wt * rm_rate / sheet_nest_data[4]
        return round(opt_rm_cost, 2)
    def get_fright_cost(self, rm_cost, fright_percent=0.03):
        rm_fright_cost = rm_cost * fright_percent
        return round(rm_fright_cost, 2)
    def get_rejection_cost(self, rm_cutting_cost, rejection_percent=0.01):
        rejection_cost = rm_cutting_cost * rejection_percent
        return round(rejection_cost, 2)
    def get_area(self, blank_size):
        area = blank_size[0] * blank_size[1]
        return area
    def get_post_process_cost(self, area,thickness,density, pp_rate):
        # post_process_cost = (area * pp_rate * 2)/645.16
        post_process_cost = (area * thickness * density * pp_rate)/1000000
        return post_process_cost
    def get_bending_cost(self,mf_bend,no_of_bends):
        bend_cost = float(no_of_bends) * float(mf_bend)
        return bend_cost
    def sheet_maetal_cost(self,data):
        nos = data["nos"]
        sheet_data = {}
        perimeter = data["perimeter"]
        no_of_start = data["no_of_start"]
        blank_size = data["box_size"]
        sheet_nest_data = self.nesting_sheet_size(
            blank_size, data["sheet_size"], nos, mesh_size=312.5)
        area = self.get_area(blank_size)
        volum = self.get_total_volume(
            sheet_nest_data, data["sheet_size"], data["thk"])
        wt = self.get_total_wt(volum, data["density"])
        wt_per_part = self.get_wt(wt, nos)
        rm_cost = self.get_rm_cost(wt_per_part, data['rm_rate'])
        opt_rm_cost = self.optimun_rm_cost(
            wt, sheet_nest_data, data["rm_rate"])
        l_cut_cost = self.get_cutting_cost(
            data["c_mf"], perimeter, data["thk"], no_of_start, data["ns_mf"])
        rm_cutting_cost = rm_cost + l_cut_cost
        rm_fright_cost = self.get_fright_cost(rm_cost, fright_percent=float(data["fright_percent"]),)
        rejection_cost = self.get_rejection_cost(
            rm_cutting_cost, rejection_percent=float(data["rejection_percent"]))
        bending_cost = 0
        post_processing_cost = 0
        if data["sub_process"] == "Laser Cutting":
            if data["surface_finish"] in ["Buffing - Matte", "Buffing - Glossy", "Powder Coating", "Zinc Plating", "Anodising"]:
                post_processing_cost = self.get_post_process_cost(
                    area,data["thk"], data["density"], data["pp_rate"])
                total_cost_per_part = rm_cutting_cost + \
                    rm_fright_cost + rejection_cost + post_processing_cost
                total_cost = total_cost_per_part * nos
                opt_total_cost_per_part = opt_rm_cost + l_cut_cost + \
                    rm_fright_cost + rejection_cost + post_processing_cost
                opt_total_cost = opt_total_cost_per_part * sheet_nest_data[4]
            else:
                total_cost_per_part = rm_cutting_cost + rm_fright_cost + rejection_cost
                total_cost = total_cost_per_part * nos
                opt_total_cost_per_part = opt_rm_cost + \
                    l_cut_cost + rm_fright_cost + rejection_cost
                opt_total_cost = opt_total_cost_per_part * sheet_nest_data[4]
        elif data["sub_process"] == "Laser Cutting & Bending":
            if data["surface_finish"] in ["Buffing - Matte", "Buffing - Glossy", "Powder Coating", "Zinc Plating", "Anodising"]:
                bending_cost = self.get_bending_cost(
                    data["mf_bend"], data["no_of_bend"])
                post_processing_cost = self.get_post_process_cost(
                    area, data["thk"], data["density"], data["pp_rate"])
                total_cost_per_part = rm_cutting_cost + rm_fright_cost + \
                    rejection_cost + bending_cost + post_processing_cost
                total_cost = total_cost_per_part * nos
                opt_total_cost_per_part = opt_rm_cost + l_cut_cost + rm_fright_cost + \
                    rejection_cost + bending_cost + post_processing_cost
                opt_total_cost = opt_total_cost_per_part * sheet_nest_data[4]
            else:
                bending_cost = self.get_bending_cost(
                    data["mf_bend"], data["no_of_bend"])
                total_cost_per_part = rm_cutting_cost + \
                    rm_fright_cost + rejection_cost + bending_cost
                total_cost = total_cost_per_part * nos
                opt_total_cost_per_part = opt_rm_cost + l_cut_cost + \
                    rm_fright_cost + rejection_cost + bending_cost
                opt_total_cost = opt_total_cost_per_part * sheet_nest_data[4]
        else:
            return "Manual quote will provide."
        # sheet_data["file_name"] = str(path).split("\\")[-1]
        sheet_data["perimeter"] = round(perimeter, 2)
        sheet_data["no_of_start"] = no_of_start
        sheet_data["blank_size"] = blank_size
        sheet_data["nest_blank_size"] = sheet_nest_data[2]
        sheet_data["no_of_sheet"] = sheet_nest_data[0]
        sheet_data["sheet_thickness"] = data["thk"]
        sheet_data["area"] = area
        sheet_data["volume"] = volum
        sheet_data["wt"] = wt
        sheet_data["nos"] = sheet_nest_data[1]
        sheet_data["wt_per_part"] = wt_per_part
        sheet_data["rm_cost"] = rm_cost
        sheet_data["lasser_cutting_cost"] = l_cut_cost
        sheet_data["rm_cutting_cost"] = rm_cutting_cost
        sheet_data["rm_fright_cost"] = rm_fright_cost
        sheet_data["rejection_cost"] = rejection_cost
        sheet_data["bending_cost"] = bending_cost
        sheet_data["post_processing_cost"] = post_processing_cost
        sheet_data["total_cost_per_part"] = total_cost_per_part
        sheet_data["total_cost"] = total_cost
        sheet_data["optimum_nos"] = sheet_nest_data[4]
        sheet_data["optimum_rm_cost"] = opt_rm_cost
        sheet_data["optimum_total_cost_per_part"] = opt_total_cost_per_part
        sheet_data["optimum_total_cost"] = opt_total_cost
        return sheet_data


