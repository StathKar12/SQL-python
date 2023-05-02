# ----- CONFIGURE YOUR EDITOR TO USE 4 SPACES PER TAB ----- #
import settings
import sys,os
sys.path.append(os.path.join(os.path.split(os.path.abspath(__file__))[0], 'lib'))
import pymysql as db
import random
random.seed(1)

def connection():
    ''' User this function to create your connections '''
    con = db.connect(
        settings.mysql_host, 
        settings.mysql_user, 
        settings.mysql_passwd, 
        settings.mysql_schema)
    
    return con

def mostcommonsymptoms(vax_name):
    
    int_VN = int(vax_name)
    # Create a new connection
    # Create a new connection
    con=connection()
    # Create a cursor on the connection
    cur=con.cursor()
    
    
    
    return [("vax_name","result")] 


def buildnewblock(blockfloor):
    
   # Create a new connection
    con=connection()
    
    # Create a cursor on the connection
    cur=con.cursor()
    if  not blockfloor:
        blockfloor='0'
    #Checking Floor's existence and wards
    sql="select BlockFloor,count(BlockCode) from block where BlockFloor=%s;"%(blockfloor)

    cur.execute(sql)
    ((Floor,Wards),) = cur.fetchall()
    
    #Checking if we can add a Ward
    if(Wards == 9):
        result=[("--Floor %s has 9 Wards--"%(blockfloor),)]
    elif (int(blockfloor) > 7) or (int(blockfloor) < 1):
        result=[("--The Hospital has 1,2,3,4,5,6,7 floors--",)]
    else:#Adding the Ward
        ExistedWard=(True)
        BlockCode=0
        while ExistedWard:#Searching for Ward's Code
            BlockCode += 1
            sql="""select distinct %d from block b where b.BlockCode=%d and b.BlockFloor=%d;"""%(BlockCode,BlockCode,Floor)
            cur.execute(sql)
            ExistedWard=cur.fetchall()
        
        #Adding the Ward in the block
        sql="""insert into block (BlockFloor,BlockCode)
	    values (%d,%d);"""%(Floor,BlockCode)
        cur.execute(sql)
        con.commit()

        #Creating First RoomNumber
        roomNumber=blockfloor+str(BlockCode) +"00"
        roomNumber=int(roomNumber)
        Rooms = random.randint(1,5)
        RoomTypes=["single","double","triple","quadruple"]

        #Inserting new rooms in the new Ward
        for room in range(Rooms) :
            roomType=random.choice(RoomTypes)
            availability=random.randint(0,1)
            sql="""insert into room (RoomNumber,RoomType,BlockFloor,BlockCode,Unavailable)
	            values (%s,"%s",%d,%d,%d);"""%(roomNumber,roomType,Floor,BlockCode,availability)
            cur.execute(sql)
            con.commit()
            roomNumber +=1

        #Searching for the result of our actions, helping the user to see the changes made 
        sql="select * from room where BLockFloor=%d and BlockCode=%d order by RoomNumber;"%(Floor,BlockCode)
        cur.execute(sql)
        result = cur.fetchall()

    
    result = list(result)
    return [("RoomNumber", "RoomType", "BlockFloor", "BlockCode", "Unavailable")] + result

def findnurse(x,y):

    # Create a new connection
    
    con=connection()
    
    # Create a cursor on the connection
    cur=con.cursor()
    if not x:
        x=0
    if not y:
        y=0
    
    sql = """select distinct n.Name, n.EmployeeID,
	(select count(distinct vac.patient_SSN) from vaccination vac where n.EmployeeID=vac.nurse_EmployeeID) as Patients
	from nurse n where %s =any (select distinct b.BlockFloor from block b )
	and (select count(distinct oc.BlockCode) from on_call oc where n.EmployeeID=oc.nurse and oc.BlockFloor=%s) =  
    (select count(distinct oc.BlockCode) from on_call oc where oc.BlockFloor=%s) 
    and %s <= (select count(ap.Patient) from appointment ap where n.EmployeeID=ap.PrepNurse) ;""" %(x,x,x,y)
    
    cur.execute(sql)
    result = cur.fetchall()
    if(result == ()):
        result=[("--No results--",)]
    result = list(result)
    return [("Nurse", "ID", "Number of patients")] + result

def patientreport(patientName):
    # Create a new connection
    con=connection()

    # Create a cursor on the connection
    cur=con.cursor()


    sql=f"""select 
	 p.Name as Patient,
	 ph.Name as Physician,
     n.Name as Nurse,
     t.Name as "Treatment going on",
     t.Cost as Cost,
     st.StayEnd as "Date of release",
     st.Room as Room,
     r.BlockFloor as Floor,
     r.BlockCode  as Ward
     from undergoes u, patient p, physician ph, nurse n, treatment t, stay st, room r
		where p.SSN=u.Patient  
        and ph.EmployeeID=u.Physician
		and n.EmployeeID=u.AssistingNurse 
        and t.Code=u.Treatment
        and st.StayID=u.Stay
        and r.RoomNumber=st.Room
    group by u.Patient
    having u.Patient = any(select SSN from patient where Name like "%{patientName}%"); """

    cur.execute(sql)
    result = cur.fetchall()
    if(result == ()):
        result=[("--No results--",)]
    result = list(result)

    return [("Patient","Physician", "Nurse", "Treatement going on", "Cost", "Date of release", "Room", "Floor", "Block")] + result

