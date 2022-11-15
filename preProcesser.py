import Prom_project, Prom_scope, Prom_specification
import Prom_ref_tag, Prom_ref_status, Prom_ref_duration
import Oms_payment_monitoring
import Fms_payment
import Employee

from java.util import ArrayList
from java.util import HashMap
from java.math import BigDecimal
from java.math import RoundingMode

if request.getParameter("msg"):
    output["msg"] = request.getParameter("msg")

statusList = Prom_ref_status.findAll()
output["statusList"] = statusList

# paymentList = Oms_payment_monitoring.findAll()
# output["paymentList"] = paymentList

# paymentFile = Fms_payment.findAll().orderBy("payment_id asc")
# output["paymentFile"] = paymentFile

employeeList = Employee.findAll()
specList = Prom_specification.findAll()
projectList = Prom_project.findAll()
proList = HashMap()

loggedPerson = Employee.first("login_id = ?", user.getLoginId())

for p in projectList:
    groupSpec = Prom_specification.findBySQL("""select count(*) as count, sum(pd.value_days) as total_days, avg(percentage) as percentage,scope_id, pc.project_id as pro_id 
    from prom_specification ps,prom_ref_duration pd, prom_scope pc where ps.unit_id = pd.id and pc.id = ps.scope_id and pc.project_id = ? group by scope_id""", p.get("id")).toMaps()
    for grp in groupSpec:
        # print grp
        avg = BigDecimal(str(grp.get("percentage"))).setScale(1, BigDecimal.ROUND_HALF_UP)
        # print avg
        if avg == BigDecimal("100.00"):
            clz = "bg-success"
        elif avg > BigDecimal("75.00"):
            clz = "bg-info"
        elif avg > BigDecimal("50.00"):
            clz = "bg-warning"
        else:
            clz = "bg-danger"
        grp.put("clz", clz)
        grp.put("avg", avg)
    project = HashMap()
    project.put("grpSpec" , groupSpec)
    project.put("id" , p.get("id"))
    proList.put(p.get("id") ,project)

# print proList
output["proList"] = proList

isAdmin = 1

specs = ArrayList()
for spec in specList:
    spec = spec.toMap()
    if not isAdmin:
        if spec.get("status_id") > 1:
            spec.put("updatable", 1)
        if spec.get("assigned_id") == loggedPerson.getId():
            spec.put("isPIC", 1)
    else:
        spec.put("updatable", 1)
        spec.put("isPIC", 1)
        
    specs.add(spec)

output["specList"] = specs
output["tags"] = Prom_ref_tag.findAll()
output["groupSpec"] = groupSpec

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

output["projectList"] = projectList

scopeList = Prom_scope.findAll()
durationList = Prom_ref_duration.findAll()

output["scopeList"] = scopeList
output["employeeList"] = employeeList
output["durationList"] = durationList
