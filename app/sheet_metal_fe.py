import ezdxf
import math
import numpy as np

def get_dxf_perimeter(path) :   
    dwg = ezdxf.readfile(path)
    msp = dwg.modelspace()
    longitud_total = 0
    for e in msp:
        if e.dxftype() == 'LINE' and e.dxf.linetype in ['Continuous','ByLayer']:
            dl = math.sqrt((e.dxf.start[0]-e.dxf.end[0])**2 + (e.dxf.start[1]- 
            e.dxf.end[1])**2)
            longitud_total = longitud_total + dl
        elif e.dxftype() == 'CIRCLE' and e.dxf.linetype in ['Continuous','ByLayer']:
            dc = 2*math.pi*e.dxf.radius
            longitud_total = longitud_total + dc
        elif e.dxftype() == 'ARC' and e.dxf.linetype in ['Continuous','ByLayer']:
            angle = abs(e.dxf.start_angle -e.dxf.end_angle)
            arc_perimeter = 2*math.pi*e.dxf.radius*angle/360        
            longitud_total = longitud_total + arc_perimeter
#         elif e.dxftype() == 'SPLINE' and e.dxf.linetype== 'Continuous':
#             puntos = e.get_control_points()
#             for i in range(len(puntos)-1):
#                 ds = math.sqrt((puntos[i][0]-puntos[i+1][0])**2 + (puntos[i][1]- 
#                 puntos[i+1][1])**2)  
#                 longitud_total = longitud_total + ds
    for indx,x in enumerate(msp.query('SPLINE')):
        s_point = x.control_points
        for i in range(len(s_point)-1):
                ds = math.sqrt((s_point[i][0]-s_point[i+1][0])**2 + (s_point[i][1]- 
                s_point[i+1][1])**2)  
    #             print('curva: '+str(ds))
                longitud_total = longitud_total + ds
    for idx, line in enumerate(msp.query('LWPOLYLINE')): 
        coordinates = np.asarray(line)
        vertex_dist =[]
        for l in range(coordinates.shape[0]):
            try:
                vertex_diff = coordinates[l+1]-coordinates[l] 
                vertex_dist.append(math.sqrt(math.pow(vertex_diff[0],2)+math.pow(vertex_diff[1],2)))
            except:
                pass
        lwpolyline_dist = sum(vertex_dist)
        longitud_total = longitud_total + lwpolyline_dist
                
    return longitud_total

def get_no_of_start(path):
    dwg = ezdxf.readfile(path)
    msp = dwg.modelspace()
    loop_count=0
    data={}
    for e in msp:
        if e.dxf.linetype in ['Continuous','ByLayer'] and e.dxftype() == 'CIRCLE':
            loop_count+=1
        elif e.dxf.linetype in ['Continuous','ByLayer'] and e.dxftype() == 'ARC':
            start = round(e.dxf.center[0]+e.dxf.radius*math.cos(e.dxf.start_angle*math.pi/180),2),round(e.dxf.center[1]+e.dxf.radius*math.sin(e.dxf.start_angle*math.pi/180),2)
            end = round(e.dxf.center[0]+e.dxf.radius*math.cos(e.dxf.end_angle*math.pi/180),2),round(e.dxf.center[1]+e.dxf.radius*math.sin(e.dxf.end_angle*math.pi/180),2)
            data[str(e)]= start,end,e.dxftype()
        elif e.dxf.linetype in ['Continuous','ByLayer'] and e.dxftype() == 'LINE':
            start = round(e.dxf.start[0]),round(e.dxf.start[1])
            end = round(e.dxf.end[0]),round(e.dxf.end[1])
            data[str(e)]= start,end,e.dxftype()
    for idx, line in enumerate(msp.query('LWPOLYLINE')):
        coordinates = np.asarray(line)
        start = round(coordinates[0][0],2),round(coordinates[0][1],2)
        end = round(coordinates[-1][0],2),round(coordinates[-1][1],2)
        data['LWPOLYLINE'+ "_"+str(idx)]= start,end,'LWPOLYLINE'
    def start_entity(entity):
        for e in data.keys():            
            if str(entity) != str(e): 
                if (abs(data[str(entity)][0][0] - data[str(e)][0][0])<.6) and (abs(data[str(entity)][0][1] - data[str(e)][0][1])<.6):
                    return e,"start"
                elif (abs(data[str(entity)][0][0] - data[str(e)][1][0])<.6) and (abs(data[str(entity)][0][1] - data[str(e)][1][1])<.6):
                    return e, "end"
    def end_entity(entity):
        for e in data.keys():            
            if str(entity) != str(e): 
                if (abs(data[str(entity)][1][0] - data[str(e)][0][0])<.6) and (abs(data[str(entity)][1][1] - data[str(e)][0][1])<.6):
                    return e,"start"
                elif (abs(data[str(entity)][1][0] - data[str(e)][1][0])<.6) and (abs(data[str(entity)][1][1] - data[str(e)][1][1])<.6):
                    return e,"end"
    def loop(ittrate):
        if ittrate[1]=="start":
            return end_entity(ittrate[0])
        else :
            return start_entity(ittrate[0])
    loop_entity=[]
    for x in data.keys():
        if x not in loop_entity:
            loop_entity.append(x)
            var_ent=end_entity(x)
            loop_entity.append(var_ent[0])
            for lenght in range(len(data.keys())):
                var_ent = loop(var_ent)
                loop_entity.append(var_ent[0])
                if var_ent[0]== x:
                    break
                loop_entity.append(var_ent[0])
            loop_count+=1

    if loop_count == 0:
        return loop_count + 1
    else:
        return loop_count

def get_blank_size(path):
    dwg = ezdxf.readfile(path)
    msp = dwg.modelspace()
    dxf_vertex_points = []
    step_arc = 10
    step_circle = 20
    
    def step_vertex(entity,step_angle,step):
        x_vertex = entity.dxf.radius *math.cos(math.radians(step_angle*(step+1))) + entity.dxf.center[0]
        y_vertex = entity.dxf.radius *math.cos(math.radians(step_angle*(step+1))) + entity.dxf.center[1]
        return x_vertex,y_vertex
    
    for e in msp:
        if e.dxf.linetype in ['Continuous','ByLayer'] and e.dxftype() == 'CIRCLE':
            angle = 360/step_circle
            for step_len in range(step_circle-1):
                vertex = list(step_vertex(e,angle,step_len))
                dxf_vertex_points.append(vertex)
        elif e.dxf.linetype in ['Continuous','ByLayer'] and e.dxftype() == 'ARC':
            angle =abs(e.dxf.start_angle - e.dxf.end_angle)/ step_arc 
            for step_len in range(step_arc-1):
                vertex = step_vertex(e,angle,step_len)
                dxf_vertex_points.append(list(vertex))  
        elif e.dxf.linetype in ['Continuous','ByLayer'] and e.dxftype() == 'LINE':
            start = round(e.dxf.start[0]),round(e.dxf.start[1])
            end = round(e.dxf.end[0]),round(e.dxf.end[1])
            dxf_vertex_points.append(list(start))
            dxf_vertex_points.append(list(end))
            
    dxf_vertex_points = np.asarray(dxf_vertex_points).astype(float)
    
    for idx, line in enumerate(msp.query('LWPOLYLINE')):
        vertex_points = np.asarray(line)
        try:
            dxf_vertex_points = np.concatenate([dxf_vertex_points, vertex_points[:,0:2]])
        except:
            dxf_vertex_points = np.concatenate([vertex_points[:,0:2]])
        
    for indx,x in enumerate(msp.query('SPLINE')):
        s_point = x.control_points
        vertex_points = np.asarray(s_point)
#         print(vertex_points[:2].shape)
        try:
            dxf_vertex_points = np.concatenate([dxf_vertex_points, vertex_points[:,0:2]])
        except:
            dxf_vertex_points = np.concatenate([vertex_points[:,0:2]])
        
    vertices_data = np.array(dxf_vertex_points)
    x_min=np.amin(vertices_data[:,0])
    y_min=np.amin(vertices_data[:,1])
    x_max=np.amax(vertices_data[:,0])
    y_max=np.amax(vertices_data[:,1])
    
#     Calculate the Box dim
    def measure(min_,max_):
        dist = max_ - min_
        return dist
    
#     Finding the Box Dimension:
    length = round(measure(x_min,x_max),3)
    width = round(measure(y_min,y_max),3)
    return length, width

# def get_html(path):
#     # dwg = CQ(import_dxf(path))
#     dwg = ezdxf.readfile(path)
#     # svg_drawing = dwg.to_svg()
#     # html = dwg.to_html()
#     # html = svg_drawing.getvalue()
#     return dwg