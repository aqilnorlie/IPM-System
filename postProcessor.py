# SELECT e.id, e.full_name
# FROM employee e JOIN prom_project_team t ON t.emp_id = e.id 
# WHERE t.emp_id NOT IN (SELECT s.assigned_id FROM prom_specification s)

import Prom_project, Prom_scope, Prom_specification
import Prom_ref_tag, Prom_ref_duration, Prom_ref_status
import Prom_specification_log, Prom_j_spec_tag
import Prom_project_team, Prom_junction_project_team
import Prom_project_file, Prom_ref_file_category
import View_prom_project_team
import Employee

import json

from java.util import Date
from java.util import EnumSet
from java.util import HashMap
from java.util import ArrayList
from org.joda.time import DateTime
from org.joda.time import DateTimeConstants
from java.time import DayOfWeek
from java.time import LocalDate
from java.time.temporal import ChronoUnit
from java.math import BigDecimal
from org.javalite.activejdbc import Base

d_action = request.getParameter("d_action")

today = Date()

def saveJobHistory(action, jobId, remark):
    log = Prom_specification_log()
    log.set("spec_id", jobId)
    log.set("log_type", 4) # 4 fr TR
    log.set("update_date", today)
    log.set("update_by", user.getLoginId())
    log.set("action", action)
    log.set("remarks", remark)
    log.saveIt()


def add(startDate, workdays):
    if workdays < 1:
        return startDate
    
    endDate = startDate
    addedDays = 0
    while (addedDays < workdays):
    # for x in range workdays:
        endDate = endDate.plusDays(1)
        print endDate.toString("dd-MM-yyyy")
        if (endDate.dayOfWeek().get() == DateTimeConstants.SATURDAY or endDate.dayOfWeek().get() == DateTimeConstants.SUNDAY):
            print "skipped"
            
            
        else:
            addedDays =  addedDays + 1
            print "count : " + str(addedDays)
            
    return endDate
    
def countWeekDays (startDate, endDate):
    count = 0
    startW = startDate.getDayOfWeek()
    stopW = endDate.getDayOfWeek()

    days = ChronoUnit.DAYS.between( startDate , endDate )
    print days
    print startW.getValue()
    daysWithoutWeekends = days - 2 * ( ( days + startW.getValue() ) / 7 )

    
    print daysWithoutWeekends
    # if mode == 2:
    #     print "cuti jumaat sabtu"
    #     # //adjust for starting and ending on a SATURDAY (johor, kelantan):
    #     if (startW == DayOfWeek.SATURDAY):
    #         x = 1
    #     else:
    #         x = 0
            
    #     if (stopW == DayOfWeek.SATURDAY):
    #         y = 1
    #     else:
    #         y = 0
    # else:
        # //adjust for starting and ending on a Sunday.. by default
    if (startW == DayOfWeek.SUNDAY):
        x = 1
    else:
        x = 0
        
    if (stopW == DayOfWeek.SUNDAY):
        y = 1
    else:
        y = 0
            
    # count = daysWithoutWeekends + 1 if (startW == DayOfWeek.SUNDAY) else 0 + 1 if (stopW == DayOfWeek.SUNDAY) else 0 
    count = daysWithoutWeekends + x + y
    print "total working days (nor): " + str(count)
    return count


def countSpecialWeekend (startDate, endDate):
    count = 0
    weekend = EnumSet.of( DayOfWeek.FRIDAY , DayOfWeek.SATURDAY )
    ld = startDate
    while ( ld.isBefore( endDate ) ):
        if not (weekend.contains(ld.getDayOfWeek())):
            count = count + 1
        else:
            print "weeekenddd : " + str(ld.getDayOfWeek())
        ld = ld.plusDays(1)
        
    print "total working days (sp): " + str(count)
    return count
    
# Save newly added specification
if d_action == "save":
    form_data = json.loads(data_form)
    
    # check if spec. name is used
    spec_name = str(form_data["name"]).lower()
    allSpec = Prom_specification.where("project_id = ?", project_id)
    specExist = 0
    specNameList = []
    for spec in allSpec:
        specNameList.append(str(spec.get("name")).lower())
    
    if (spec_name in specNameList):
        specExist = 1
        output["specExist"] = 1
        
    if (specExist == 0):
        prom_specification = Prom_specification()
        prom_specification.set("scope_id", form_data["scope"])
        prom_specification.set("name", form_data["name"])
        prom_specification.set("description", form_data["desc"])
        prom_specification.set("unit_id", form_data["duration"])
        prom_specification.set("assigned_id", form_data["assignedPerson"])
        prom_specification.set("added_date", today)
        specScope = Prom_scope.findFirst("id = ?", form_data["scope"])
        projectId = specScope.get("project_id")
        prom_specification.set("project_id", projectId)
        prom_specification.saveIt()
        
        # if request.get("tag"):
        if form_data["tag"]:
            for t in form_data["tag"]:
                jt = Prom_j_spec_tag()
                jt.set("spec_id", prom_specification.getId())
                jt.set("tag_id", t)
                jt.saveIt()
        
        id_spec_custom = 'sp' + str(prom_specification.get('id'))
        update = Prom_specification.findFirst('id = ?', prom_specification.get('id'))
        update.set("id_spec_custom", id_spec_custom)
        update.saveIt()
    
    # saveJobHistory("NEW", prom_specification.getId(), "")
    # go_to = "%s/t/IPM/copyds" % (ctxPath)

if d_action == "update_percentage":
    # heute = DateTime()
    # endDt = add(heute, 7)
    # print endDt.toString("dd-MM-yyyy")
    sD = LocalDate.of( 2021 , 2 , 20 )
    eD = LocalDate.of( 2021 , 2 , 24 )
    print countWeekDays(sD, eD)
    
    print countSpecialWeekend(sD, eD)
    
    
    print percentage_progress
    prom_specification = Prom_specification.findById(spec_id)
    prom_specification.set("percentage", percentage_progress)
    prom_specification.set("remarks", remarks)
    action ="UPDATE"
    if int(percentage_progress) == 100:
        action = "COMPLETE"
        prom_specification.set("status_id", 3)
    elif int(percentage_progress) < 100 and int(percentage_progress) > 0:
        action = "UPDATE"
        prom_specification.set("status_id", 2)
        
    prom_specification.saveIt()
    
    # saveJobHistory(action, spec_id, remarks)
    go_to = "%s/t/IPM/copyds" % (ctxPath)
    
if d_action == "start_job":
    
    prom_specification = Prom_specification.findById(spec_id)
    prom_specification.set("status_id", 2)
    prom_specification.saveIt()
    
    # saveJobHistory("STARTED", spec_id, "")
    go_to = "%s/t/IPM/copyds" % (ctxPath) 

if d_action == "remove_spec":
    prom_specification = Prom_specification.findById(spec_id)
    prom_specification.delete()
    
    # saveJobHistory("REMOVE", spec_id, "")
    go_to = "%s/t/IPM/copyds" % (ctxPath)      

# IGNORE !- 
# if d_action == "update_scope":
#     print scope_id
#     prom_scope = Prom_scope.findById(scope_id)
#     prom_scope.set("name", scope_name)
#     prom_scope.set("note", scope_note)
#     action ="UPDATE_SCOPE"

        
#     prom_scope.saveIt()
    
#     # saveJobHistory(action, scope_id, remarks)
#     go_to = "%s/t/IPM/copyds" % (ctxPath)
# IGNORE --
    
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

if d_action == "update_page":
    
    project_id = project
    output["project_id"] = project_id
    
    # for SCOPE in modal ADD SPECIFICATION
    projectScope = Prom_scope.where("project_id = ?", project_id)
    output["projectScope"] = projectScope
    
    # for EMPLOYEE in modal ADD SPECIFICATION
    teamMember = Base.findAll("""
    SELECT e.full_name, e.id
    FROM employee e
    JOIN prom_project_team t ON e.id = t.emp_id
    JOIN prom_junction_project_team j ON j.project_team_id = t.id
    WHERE j.project_id = %s
    """ % project_id)
    output["teamMember"] = teamMember
    
    # data for table
    promScopeAll = Prom_scope.findAll()
    promSpec = Prom_specification.where("project_id = ?", project_id)
    dataForTableArr = ArrayList()
    for a in promSpec:
        dataForTableMap = HashMap()
        # 1. id
        dataForTableMap.put("id", a.get("id"))
        # 2. spec name
        dataForTableMap.put("name", a.get("name"))
        # 3. scope name
        promScope = Prom_scope.findFirst("id = ?", a.get("scope_id"))
        scopeName = promScope.get("name")
        dataForTableMap.put("scopeName", scopeName)
        # 4. duration
        duration = Prom_ref_duration.findFirst("id = ?", a.get("unit_id"))
        durationName = duration.get("name")
        dataForTableMap.put("duration", durationName)
        # 5. assigned to
        assignedEmp = Employee.findFirst("id = ?", a.get("assigned_id"))
        assignedEmpName = assignedEmp.get("full_name")
        dataForTableMap.put("assignedTo", assignedEmpName)
        # 6. progress
        dataForTableMap.put("progressPercent", a.get("percentage"))
        # 7. status
        status = Prom_ref_status.findFirst("id = ?", a.get("status_id"))
        statusName = status.get("name")
        dataForTableMap.put("statusName", statusName)
        
        dataForTableArr.add(dataForTableMap)
        
    output["specList"] = dataForTableArr
    
    # data for simple bar chart
    projectList = Prom_project.where("id = ?", project_id)
    specList = Prom_specification.findAll()
    dataForBarArr = ArrayList()
    for a in projectList:
        projectId = a.get("id")
        dataForBarMap = HashMap()
        dataForBarMap.put("project_id", a.get("id"))
        dataForBarMap.put("project_name", a.get("name"))
        totalPercentagePerScopeMap = HashMap()
        totalPercentagePerProject = 0.00
        countScope = 0
        for b in promScopeAll:
            if b.get("project_id") == projectId:    
                scopeId = b.get("id")
                totalPercentagePerScope = 0.00
                countScope += 1
                countSpec = 0
                for c in specList:
                    if c.get("project_id") == projectId and c.get("scope_id") == scopeId:
                        totalPercentagePerScope += float(c.get("percentage"))
                        countSpec += 1
                if countSpec != 0:
                    divSpec = totalPercentagePerScope / (countSpec * 100)
                    multipliedSpec = '{:.2f}'.format(divSpec * 100)
                    totalPercentagePerScopeMap.put(b.get("name"), multipliedSpec)
                    totalPercentagePerProject += float(multipliedSpec)
                else:
                    totalPercentagePerScopeMap.put(b.get("name"), '{:.2f}'.format(0.00))
        if countScope != 0:
            divPro = totalPercentagePerProject / (countScope * 100)
            multipliedPro = '{:.2f}'.format(divPro * 100)
            dataForBarMap.put("total_percentage", multipliedPro)
            dataForBarMap.put("scope_percentage", totalPercentagePerScopeMap)
            dataForBarArr.add(dataForBarMap)
        else:
            dataForBarMap.put("total_percentage", '{:.2f}'.format(0.00))
            dataForBarMap.put("scope_percentage", totalPercentagePerScopeMap)
            dataForBarArr.add(dataForBarMap)
        
    output["dataForBar"] = dataForBarArr
    
    # START - RIGHT SIDE
    
    get_name_project = Base.findAll("select name from prom_project where id=%s" % project_id)
    get_name_manager = Base.findAll("select * from prom_junction_project_team p join prom_project_team e on p.project_team_id = e.id join employee s on s.id= e.emp_id where project_id = %s and team_id is null" % project_id)
    
    # to get id employee and name based on project id 
    get_team = Base.findAll("select DISTINCT e.full_name, e.id from prom_junction_project_team p join prom_project_team s on s.id = p.project_team_id join employee e on e.id = s.emp_id where s.team_id IS not NULL and p.project_id = %s" % project_id)
    # get all member with manager
    all_team = Base.findAll("select DISTINCT e.full_name, e.id from prom_junction_project_team p join prom_project_team s on s.id = p.project_team_id join employee e on e.id = s.emp_id where p.project_id = %s" % project_id)
    get_all_project_id = Base.findAll("select * from prom_junction_project_team p join prom_project_team s on s.id = p.project_team_id join employee e on e.id = s.emp_id join prom_specification i on s.emp_id = i.assigned_id where s.team_id IS not NULL and p.project_id = %s" % project_id)
    specListProject = Prom_specification.where("project_id = ?", project_id)
 
    task_dict = {}
    list_task = []
    head = {}
    percentage = []
    pMap = HashMap()
    emp_map = HashMap()
    name_task = HashMap()

    # for e in all_team:
    #     for i in specListProject:
    #         if i.get("assigned_id") == e.get("id"):
    #              list_task.append(i.get("name"))
    #              percentage.append(i.get("percentage"))
    #              task_dict = percentage
    #              head = {"task" : list_task, "percent" : task_dict}
    #              emp_map.put(e.get("full_name"), head)
    #     percentage = []
    #     list_task = []
    #     head = {}
    
    # for e in all_team:
    #     for i in specListProject:
    #         if i.get("assigned_id") == e.get("id"):
    #             list_task.append(i.get("name"))
    #             name_task.put(e.get("full_name"), list_task)
    #         else:
    #             name_task.put(e.get("full_name"), list_task)
    #     list_task = []
    
    ############################################################################
    
    for e in all_team:
        if specListProject:
            for i in specListProject:
                if i.get("assigned_id") == e.get("id"):
                    list_task.append(i.get("name"))
                    name_task.put(e.get("full_name"), list_task)
                else:
                    name_task.put(e.get("full_name"), list_task)
        else:
            name_task.put(e.get("full_name"), list_task)
        list_task = []
        
    ##################################################################
    
    all_task = []
    dict_data = {}
    for e in all_team:
        dict_data[e.get("full_name")] = {}
        for i in specListProject:
            dict_data[e.get("full_name")][i.get("name")] = 0
            if i.get("assigned_id") == e.get("id"):
                dict_data[e.get("full_name")][i.get("name")] = i.get("percentage")
     
    dict_test = {}
    for i in specListProject:
        dict_test[i.get("name")] = {}
        for e in all_team:
            dict_test[i.get("name")][e.get("full_name")] = 0
            if i.get("assigned_id") == e.get("id"):
                dict_test[i.get("name")][e.get("full_name")] = i.get("percentage")
        
    output["dict_test"] = dict_test
    output["dict_data"] = dict_data
    output["project_name"] = get_name_project
    output["project_manager"] = get_name_manager
    output["team_task"] = emp_map
    output["name_task"] = name_task
    
    # END - RIGHT SIDE
    
    # START: data for TREEVIEW (PROJECT FOLDER)
    
    # FILE CATEGORY
    fileCategoryAll = Prom_ref_file_category.where('project_id = ?', project_id)
    output["fileCategoryAll"] = fileCategoryAll
    
    # FILES
    # fileList = Prom_project_file.where("project_id = ?", project_id)
    fileList = Base.findAll("SELECT * FROM prom_project_file WHERE project_id = %s" % project_id)
    for f in fileList:
        fileName = str(f.get("file_fn")).lower()
        if fileName.endswith(('.png', '.jpg', '.jpeg')):
            f.put('icon', 'fa-regular fa-file-image')
        elif fileName.endswith('.txt'):
            f.put('icon', 'fa-regular fa-file-lines')
        elif fileName.endswith('.pdf'):
            f.put('icon', 'fa-regular fa-file-pdf')
        elif fileName.endswith('.docx'):
            f.put('icon', 'fa-regular fa-file-word')
        else:
            f.put('icon', 'fa-regular fa-file')
    output["fileList"] = fileList
    
    # END: data for TREEVIEW (PROJECT FOLDER)
    
    # list of employees for modal CHANGE PROJECT MANAGER
    empAvailabeList = Base.findAll("SELECT e.id, e.full_name FROM employee e")
    output["empAvailabeList"] = empAvailabeList
    
    # START: data for TREEVIEW (OVERALL PROJECT VIEW)
    
    current_project = Base.findAll("Select id_project_custom, name from prom_project where id = %s" % project_id)
    current_scope = Base.findAll("Select s.name,s.id,s.id_scope_custom,p.id_project_custom from prom_scope s join prom_project p on s.project_id = p.id where s.project_id = %s" % project_id)
    current_spec = Base.findAll("select p.id,p.name,p.id_spec_custom,s.id_scope_custom from prom_specification p join prom_scope s on s.id = p.scope_id where p.project_id = %s" % project_id)
    output["current_project"] = current_project
    output["current_scope"] = current_scope
    output["current_spec"] = current_spec
    
    # END: data for TREEVIEW (OVERALL PROJECT VIEW)
    
if d_action == "getSpec":
    spec = Prom_specification.findById(iid)
    output["spec"] = spec
    
    # All tags
    specTagAll = Prom_ref_tag.findAll()
    output["specTagAll"] = specTagAll
    
    # for options in editing SPEC's TAG modal (chosen tag)
    specTag = Base.findAll("""SELECT t.id, t.name FROM prom_ref_tag t JOIN prom_j_spec_tag j ON t.id = j.tag_id WHERE j.spec_id = %s""" % iid)
    specArr = []
    for t in specTag:
        specArr.append(int(t.get("id")))
    output["specTag"] = specTag
    output["specArr"] = specArr
    
    # for options in editing SPEC's TAG modal (not chosen tag)
    # notSpecTag = Base.findAll("""
    # SELECT t.id, t.name FROM prom_ref_tag t
    # WHERE t.id NOT IN (SELECT t.id FROM prom_ref_tag t JOIN prom_j_spec_tag j ON t.id = j.tag_id WHERE j.spec_id = %s)""" % iid)
    # output["notSpecTag"] = notSpecTag

# update SPEC - NAME, DESC, TAG
if d_action == "update_spec":
    form_data = json.loads(data_form)
    
    # check if spec. name is used
    spec_name = str(form_data["name"]).lower()
    allSpec = Prom_specification.where("project_id = ? and id != ?", project_id, form_data["specId"])
    specExist = 0
    specNameList = []
    for spec in allSpec:
        specNameList.append(str(spec.get("name")).lower())
    
    if (spec_name in specNameList):
        specExist = 1
        output["specExist"] = 1
        
    if (specExist == 0):
        
        spec_id = form_data["specId"]
        spec_name = form_data["name"]
        spec_desc = form_data["desc"]
        tag = form_data["tag"]
        
        prom_spec = Prom_specification.findById(spec_id)
        prom_spec.set("name", spec_name)
        prom_spec.set("description", spec_desc)
        
        # Spec. HAS NO TAG
        if tag is None:
            existingTag = Prom_j_spec_tag.where("spec_id = ?", spec_id)
            for a in existingTag:
                a.delete()
        
        # Spec. HAS TAG
        elif tag != None:
            # save tag
            existingTag = Prom_j_spec_tag.where("spec_id = ?", spec_id)
            newTagIdArr = []
            existingTagIdArr = []
            for a in tag:
                newTagIdArr.append(int(a))
            # print newTagIdArr
            for b in existingTag:
                existingTagIdArr.append(int(b.get("tag_id")))
            # print existingTagIdArr
            for newTag in newTagIdArr:
                inDB = False
                # print("new tag id: ", newTag)
                for existingTag in existingTagIdArr:
                    # print("existing tag id: ", existingTag)
                    if newTag == existingTag:
                        existingTagIdArr.remove(existingTag)
                        inDB = True
                        break
                if inDB == False:
                    jt = Prom_j_spec_tag()
                    jt.set("spec_id", spec_id)
                    jt.set("tag_id", newTag)
                    jt.saveIt()
            
            # delete tag from DB
            for a in existingTagIdArr:
                delTag = Prom_j_spec_tag.findFirst("spec_id = ? and tag_id = ?", spec_id, a)
                delTag.delete()
    
        # action ="UPDATE_SPEC"
        prom_spec.saveIt()
        
    # go_to = "%s/t/IPM/copyds" % (ctxPath)

if d_action == "getScope":
    scope = Prom_scope.findById(iid)
    output["scope"] = scope

# update SPEC - SCOPE ONLY
if d_action == "updateSpecScope":
    spec = Prom_specification.findById(specIdScope)
    scope = Prom_scope.findById(specScope)
    spec.set("scope_id", specScope)
    spec.set("project_id", scope.get("project_id"))
    spec.saveIt()
    go_to = "%s/t/IPM/copyds" % (ctxPath)

# update SPEC - ASSIGNED TO ONLY
if d_action == "updateAssignedTo":
    spec = Prom_specification.findById(specIdEmp)
    spec.set("assigned_id", assignedEmp)
    spec.saveIt()
    go_to = "%s/t/IPM/copyds" % (ctxPath)

# get TEAM MEMBER for dropdown in modal ADD TEAM MEMBER
if d_action == "get_team_member":
    teamMemberOption = Base.findAll("""
    SELECT e.id, e.full_name FROM employee e WHERE e.id NOT IN
    (SELECT t.emp_id FROM prom_project_team t JOIN prom_junction_project_team j ON j.project_team_id = t.id WHERE t.team_id IS NULL AND j.project_id = %s)
    """ % project_id)
    output["teamMemberOption"] = teamMemberOption
    
    teamMember = Base.findAll("""
    SELECT e.full_name, e.id
    FROM employee e 
    JOIN prom_project_team t ON e.id = t.emp_id 
    JOIN prom_junction_project_team j ON j.project_team_id = t.id
    WHERE project_id = %s AND t.team_id IS NOT NULL
    """ % project_id)
    
    empArr = []
    for emp in teamMember:
        empArr.append(int(emp.get("id")))
    output["empArr"] = empArr

if d_action == "save_team":
    input_TM = json.loads(inputTM)
    # if (input_TM is None):
    #     print "kosong"
    # else:
    #     print "tak kosong"
    #     print(type(input_TM))
    #     print input_TM
    
    # Team HAS NO MEMBER
    if (input_TM is None):
        existingMember = Prom_junction_project_team.where("project_id = ?", team_project_id)
        for a in existingMember:
            table_team_id = a.get("project_team_id")
            row_table_team = Prom_project_team.findById(table_team_id)
            # delete team member only
            if (row_table_team.get("team_id") != None):
                emp_id = row_table_team.get("emp_id")
                specToDelete = Prom_specification.where("project_id = ? and assigned_id = ?", team_project_id, emp_id)
                for specs in specToDelete:
                    spec_id = specs.get("id")
                    specTagToDelete = Prom_j_spec_tag.where("spec_id = ?", spec_id)
                    for tags in specTagToDelete:
                        tags.delete()
                    specs.delete()
                row_table_team.delete()
                a.delete()
    
    # Team HAS MEMBER
    elif (input_TM != None):
        print input_TM
        # Save team member
        existingMember = Base.findAll("""
        SELECT t.emp_id, e.full_name, t.id FROM prom_project_team t 
        JOIN prom_junction_project_team j ON j.project_team_id = t.id JOIN employee e ON e.id = t.emp_id 
        WHERE j.project_id = %s AND t.team_id IS NOT NULL
        """ % team_project_id)
        newMemberArr = []
        existingMemberArr = []
        for a in input_TM:
            # print(int(a))
            newMemberArr.append(int(a))
        print "new member"
        print newMemberArr
        for b in existingMember:
            existingMemberArr.append(int(b.get("emp_id")))
        print "existing member"
        print existingMemberArr
        for newMember in newMemberArr:
            inDB = False
            for existingMember in existingMemberArr:
                if newMember == existingMember:
                    existingMemberArr.remove(existingMember)
                    inDB = True
                    break
            if inDB == False:
                team_id = Base.findAll("""
                SELECT t.id FROM prom_project_team t 
                JOIN prom_junction_project_team j ON j.project_team_id = t.id JOIN employee e ON e.id = t.emp_id 
                WHERE j.project_id = %s AND t.team_id IS NULL                
                """ % team_project_id)
                for a in team_id:
                    team_id = a.get("id")
                promTeam = Prom_project_team()
                promJ = Prom_junction_project_team()
                if (team_id):
                    promTeam.set("team_id", team_id)
                else: 
                    promTeam.set("team_id", 0)
                promTeam.set("emp_id", newMember)
                promTeam.saveIt()
                
                promJ.set("project_team_id", promTeam.get("id"))
                promJ.set("project_id", team_project_id)
                promJ.saveIt()
                
        # Delete team member from DB
        for a in existingMemberArr:
            rowToBeDeleted = Base.findAll("""
            SELECT t.id AS table_team_id, j.id AS table_junction_id FROM prom_project_team t JOIN prom_junction_project_team j ON j.project_team_id = t.id 
            WHERE t.emp_id = %s AND j.project_id = %s
            """ % (a, team_project_id))
            for b in rowToBeDeleted:
                table_team = Prom_project_team.findById(b.get("table_team_id"))
                emp_id = table_team.get("emp_id")
                specToDelete = Prom_specification.where("project_id = ? and assigned_id = ?", team_project_id, emp_id)
                for specs in specToDelete:
                    spec_id = specs.get("id")
                    specTagToDelete = Prom_j_spec_tag.where("spec_id = ?", spec_id)
                    for tags in specTagToDelete:
                        tags.delete()
                    specs.delete()
                table_junction = Prom_junction_project_team.findById(b.get("table_junction_id"))
                table_team.delete()
                table_junction.delete()

    # action ="UPDATE_TEAM_MEMBER"
    go_to = "%s/t/IPM/copyds" % (ctxPath)
    
if d_action == "uploadFile":
    if project_file:
        promFile = Prom_project_file()
        promFile.set("file", project_file)
        promFile.set("file_fn", project_file_fn)
        promFile.set("file_ft", project_file_ft)
        promFile.set("project_id", project_id_upload)
        promFile.set("file_category_id", file_category_id)
        promFile.saveIt()
        
        file_id_custom = 'file_' + str(promFile.get('id'))
        update = Prom_project_file.findFirst('id = ?', promFile.get('id'))
        update.set("file_id_custom", file_id_custom)
        update.saveIt()
        
    go_to = "%s/t/IPM/copyds" % (ctxPath)

if d_action == "updateTree":
    tree_data = json.loads(treeData)
    for a in tree_data:
        parent = str(a.get("parent"))
        a_attr_href = str(a.get('a_attr', {}).get('href'))
        # under a folder
        if (parent != '#'):
            # a file under folder
            if (a_attr_href != '#'):
                promFile = Prom_project_file.findFirst("file_id_custom = ?", a.get("id"))
                # file_fn
                promFile.set("file_fn", a.get("text"))
                # file_category_id
                promFile.set("file_category_id", a.get("parent"))
                promFile.saveIt()
            # a folder under folder
            else:
                promCat = Prom_ref_file_category.findFirst("file_category_id_custom = ?", a.get("id"))
                # name
                promCat.set("name", a.get("text"))
                # parent_id
                promCat.set("parent_id", a.get("parent"))
                promCat.saveIt()
        # a root folder
        else:
            promCat = Prom_ref_file_category.findFirst("file_category_id_custom = ?", a.get("id"))
            # name
            promCat.set("name", a.get("text"))
            promCat.set("parent_id", '0')
            promCat.saveIt()
            
if d_action == "deleteFile":
    fileArr = json.loads(fileDeleteArr)
    fileArrList = []
    for a in fileArr:
        fileArrList.append(str(a))
    
    for fileId in fileArrList:
        folder = Prom_ref_file_category.findFirst("file_category_id_custom = ?", fileId)
        file = Prom_project_file.findFirst("file_id_custom = ?", fileId)
        if (folder):
            # to cater if 'id' in prom_ref_file_category == 'id' in prom_file_category (DONE)
            # try:
                # print folder.get('test')
            # except:
                # print 'error'
            folder.delete()
            fileUnder = Prom_project_file.where("file_category_id = ?", fileId)
            for b in fileUnder:
                b.delete()
        elif (file):
            file.delete()
            
if d_action == "createFolderRoot":
    folder = Prom_ref_file_category()
    folder.set("name", name)
    folder.set("project_id", projectId)
    folder.set("parent_id", '0')
    folder.saveIt()
    
    file_category_id_custom = 'folder_' + str(folder.get('id'))
    output["file_category_id_custom"] = file_category_id_custom
    update = Prom_ref_file_category.findFirst('id = ?', folder.get('id'))
    update.set("file_category_id_custom", file_category_id_custom)
    update.saveIt()
    
if d_action == "createFolderChild":
    folder = Prom_ref_file_category()
    folder.set("name", name)
    folder.set("project_id", projectId)
    folder.set("parent_id", parent_id)
    folder.saveIt()
    
    file_category_id_custom = 'folder_' + str(folder.get('id'))
    output["file_category_id_custom"] = file_category_id_custom
    update = Prom_ref_file_category.findFirst('id = ?', folder.get('id'))
    update.set("file_category_id_custom", file_category_id_custom)
    update.saveIt()
    
if d_action == "update_project_manager":
    chosen_manager_emp_id = empList
    manager_team_id = managerTId
    project_id = projectIdEditManager
    prom_team = Prom_project_team.findFirst("id = ?", manager_team_id)
    
    existingMember = View_prom_project_team.where("project_id = ?", project_id)
    existingMemberList = []
    existingMemberEmpIdList = []
    for a in existingMember:
        existingMemberList.append(a)
        existingMemberEmpIdList.append(int(a.get("emp_id")))
    
    # project already have a manager (CHANGE manager)
    if (manager_team_id):
        
        # check if user actually changes the manager when clicking the update button. If not, do nothing and go back to the page.
        if (int(prom_team.get("emp_id")) != int(chosen_manager_emp_id)):
            
            # START: change EXISTING manager to an EXISTING member
            
            managerPromProjectId = 0
            for a in existingMemberList:
                # if new selected manager is already in DB (member that already exists in project team).
                if (int(chosen_manager_emp_id) == int(a.get("emp_id"))):
                    # NEW manager
                    empRow = Prom_project_team.findFirst("id = ?", a.get("prom_project_team_id"))
                    newManagerEmpId = empRow.get("emp_id")
                    # OLD manager
                    managerRow = Prom_project_team.findFirst("id = ?", manager_team_id)
                    oldManagerEmpId = managerRow.get("emp_id")
                    # swap the emp_id between the NEW and OLD manager row
                    empRow.set("emp_id", oldManagerEmpId)
                    managerRow.set("emp_id", newManagerEmpId)
                    empRow.saveIt()
                    managerRow.saveIt()
                    
                    managerPromProjectId = a.get("prom_project_team_id")
                    
            # END: change EXISTING manager to an EXISTING member
            
            # START: change EXISTING manager to a NEW member (new member is added into the project team)
                
            # new member becomes the manager (will be added into the project team) and the old manager will be a member.
            if (int(chosen_manager_emp_id) not in existingMemberList):
                # create new row in prom_project_team for old manager as member
                prom_team_new = Prom_project_team()
                prom_team_new.set("team_id", manager_team_id)
                prom_team_new.set("emp_id", prom_team.get("emp_id"))
                prom_team_new.saveIt()
                prom_team_j_new = Prom_junction_project_team()
                prom_team_j_new.set("project_team_id", prom_team_new.get('id'))
                prom_team_j_new.set("project_id", project_id)
                prom_team_j_new.saveIt()
                # set new manager in row of the old manager
                prom_team.set("emp_id", chosen_manager_emp_id)
                prom_team.saveIt()
                
                managerPromProjectId = prom_team.get("id")
            
            # END: change EXISTING manager to a NEW member (new member is added into the project team)
            
            # update team_id for members
            existingMemberUpdated = View_prom_project_team.where("project_id = ?", project_id)
            existingMemberUpdatedList = []
            for b in existingMemberUpdated:
                existingMemberUpdatedList.append(b)
            for c in existingMemberUpdatedList:
                if (c.get("team_id")):
                    rowUpdated = Prom_project_team.findById(c.get("prom_project_team_id"))
                    rowUpdated.set("team_id", managerPromProjectId)
                    rowUpdated.saveIt()
                    
        # user just click the update button without changing the manager 
        else:
            go_to = "%s/t/IPM/copyds" % (ctxPath)
            
    # add new manager for project that does not have a manager (ADD project manager)
    else:
        
        # START: set an EXISTING member to be the manager
        
        # if added manager is an existing team member
        for d in existingMemberList:
            if (int(d.get("emp_id")) == int(chosen_manager_emp_id)):
                prom_team = Prom_project_team()
                prom_team.set("emp_id", chosen_manager_emp_id)
                prom_team.saveIt()
                
                prom_team_j = Prom_junction_project_team()
                prom_team_j.set("project_team_id", prom_team.get('id'))
                prom_team_j.set("project_id", project_id)
                prom_team_j.saveIt()
                
                existingMemberUpdated = View_prom_project_team.where("project_id = ?", project_id)
                for e in existingMemberUpdated:
                    # delete duplicate row
                    if ((int(e.get("emp_id")) == int(chosen_manager_emp_id)) and (e.get("team_id") != None)):
                        rowToDeleteProject = Prom_project_team.findById(e.get("prom_project_team_id"))
                        rowToDeleteJunction = Prom_junction_project_team.findFirst("project_team_id = ?", e.get("prom_project_team_id"))
                        rowToDeleteProject.delete()
                        rowToDeleteJunction.delete()
                
                # update team_id
                existingMemberUpdated = View_prom_project_team.where("project_id = ?", project_id)
                for f in existingMemberUpdated:
                    if ((f.get("team_id") != None) and (int(f.get("emp_id")) != int(chosen_manager_emp_id))):
                        updateRow = Prom_project_team.findById(f.get("prom_project_team_id"))
                        updateRow.set("team_id", prom_team.get("id"))
                        updateRow.saveIt()
                        
        # END: set an EXISTING member to be the manager
                        
        # START: set a NEW member to be the manager
                        
        # added manager is not an existing team member
        if (int(chosen_manager_emp_id) not in existingMemberEmpIdList):
            prom_team = Prom_project_team()
            prom_team.set("emp_id", chosen_manager_emp_id)
            prom_team.saveIt()
            
            prom_team_j = Prom_junction_project_team()
            prom_team_j.set("project_team_id", prom_team.get('id'))
            prom_team_j.set("project_id", project_id)
            prom_team_j.saveIt()
            
            # update team_id
            existingMemberUpdated = View_prom_project_team.where("project_id = ?", project_id)
            for e in existingMemberUpdated:
                if (e.get("team_id") != None):
                    updateRow = Prom_project_team.findById(e.get("prom_project_team_id"))
                    updateRow.set("team_id", prom_team.get("id"))
                    updateRow.saveIt()
                    
        # END: set a NEW member to be the manager
        
    go_to = "%s/t/IPM/copyds" % (ctxPath)
    
if d_action == "delete_project_manager":
    manager_team_id = managerTId
    project_id = projectIdEditManager
    
    # delete manager in prom_project_team
    prom_team = Prom_project_team.findFirst("id = ?", manager_team_id)
    # delete manager in prom_junction_project_team
    prom_team_j = Prom_junction_project_team.findFirst("project_team_id = ?", manager_team_id)
        
    # delete manager's spec.
    specToDelete = Prom_specification.where("project_id = ? and assigned_id = ?", project_id, prom_team.get("emp_id"))
    for specs in specToDelete:
        spec_id = specs.get("id")
        specTagToDelete = Prom_j_spec_tag.where("spec_id = ?", spec_id)
        # delete specs' tag
        for tags in specTagToDelete:
            tags.delete()
        specs.delete()
    prom_team.delete()
    prom_team_j.delete()
    
    # set member team_id to 0 to cater for after when manager is deleted
    team_member_row = View_prom_project_team.where("project_id = ?", project_id)
    for row in team_member_row:
        member = Prom_project_team.findById(row.get("prom_project_team_id"))
        member.set("team_id", 0)
        member.saveIt()
    
    go_to = "%s/t/IPM/copyds" % (ctxPath)

# START: CODE AQIL

# ADD PROJECT AND PROJECT MANAGER
if d_action == "data_save":
    
    # check if project name is used
    project_name = str(projectName).lower()
    allProject = Prom_project.findAll()
    projectExist = 0
    projectNameList = []
    for project in allProject:
        projectNameList.append(str(project.get("name")).lower())
    
    if (project_name in projectNameList):
        projectExist = 1
        output["projectExist"] = 1
        
    if (projectExist == 0):
        name_project = request.get("data_form[name]")
        desc_project = request.get("data_form[desc]")
        start_project = request.get("data_form[start]")
        end_project = request.get("data_form[end]")
        project_manager = request.get("data_form[project]")
        
        temp_name = 0
        temp_manager = 0
        for i in name_project:
            temp_name = len(i)
        for i in project_manager:
            temp_manager = len(i)
        if temp_name > 0:
            prom_project = Prom_project()
            prom_project.set("name", name_project[0])
            prom_project.set("planned_start_date", start_project[0])
            prom_project.set("planned_end_date", end_project[0])
            prom_project.set("note", desc_project[0])
            prom_project.saveIt()
            custom_id = Base.findAll("select id from prom_project ORDER BY id desc limit 1")
            for i in custom_id:
                custom_concat = "p" + str(i.get("id"))
                prom_project.set("id_project_custom", custom_concat)
            prom_project.saveIt()
            
        if temp_manager > 0:
            prom_project_team = Prom_project_team()
            prom_project_team.set("emp_id", project_manager[0])
            prom_project_team.saveIt()
            
            project = Base.findAll("select id from prom_project ORDER BY id desc limit 1")
            id_team = Base.findAll("select id from prom_project_team ORDER BY id desc limit 1")
            prom_junction_project_team = Prom_junction_project_team()
            for team in id_team:
                prom_junction_project_team.set("project_team_id", team.get("id"))
            for pro_id in project:
                prom_junction_project_team.set("project_id",pro_id.get("id"))
            prom_junction_project_team.saveIt()
            
        # else:
        #     msg = "Sorry you need to enter project name and Description"  # add message in front
        #     output["msg"] = msg
        
# ADD SCOPE
if d_action == "scope_save":
    
    # check if scope name is used
    scope_name = str(scopeName).lower()
    allScope = Prom_scope.where("project_id = ?", project_id)
    scopeExist = 0
    scopeNameList = []
    for scope in allScope:
        scopeNameList.append(str(scope.get("name")).lower())
    
    if (scope_name in scopeNameList):
        scopeExist = 1
        output["scopeExist"] = 1
        
    if (scopeExist == 0):
        project_id_in_scope = request.get("data_form[project_id_in_scope]")
        scope_name = request.get("data_form[scope_name]")
        scope_start = request.get("data_form[scope_start]")
        scope_end = request.get("data_form[scope_end]")
        scope_desc = request.get("data_form[scope_desc]")
    
        prom_scope = Prom_scope()
        prom_scope.set("project_id", project_id_in_scope[0])
        prom_scope.set("name", scope_name[0])
        prom_scope.set("planned_start_date", scope_start[0])
        prom_scope.set("planned_end_date", scope_end[0])
        prom_scope.set("note", scope_desc[0])
        prom_scope.saveIt()
        custom_id = Base.findAll("select id from prom_scope ORDER BY id desc limit 1")
        for i in custom_id:
            custom_concat = "sc" + str(i.get("id"))
            prom_scope.set("id_scope_custom", custom_concat)
            prom_scope.saveIt()
    # go_to = "%s/t/IPM/copyds" % (ctxPath)

# START : MODAL UPDATE PROJECT

# GET data for PROJECT when PROJECT in OVERALL PROJECT VIEW TREE is clicked
if d_action == "get_project":
    data = request.get("id_project")
    for key in data:
        project = Prom_project.findFirst("id_project_custom = ?",key)
        project_id = project.get("id")
        name =  project.get("name")
        desc = project.get("note")
        start = project.get("planned_start_date")
        end = project.get("planned_end_date")
     
    output["project_id"] = project_id    
    output["name"] = name
    output["note"] = desc
    output["start"] = start
    output["end"] = end
    
# UPDATE PROJECT    
if d_action == "update_project":
    form_data = json.loads(formData)
        
    # check if project name is used
    updated_project_name = str(updatedProjectName).lower()
    allProject = Prom_project.where("id_project_custom != ?", form_data["id_project_custom"])
    projectExist = 0
    projectNameList = []
    for project in allProject:
        projectNameList.append(str(project.get("name")).lower())
    
    if (updated_project_name in projectNameList):
        projectExist = 1
        output["projectExist"] = 1
    
    if (projectExist == 0):
        id_custom = form_data["id_project_custom"]
        name = form_data["project_name"]
        desc = form_data["project_desc"]
        start = form_data["project_start"]
        end = form_data["project_end"]
        # for i in id_custom:
        update_project = Prom_project.findFirst('id_project_custom = ?', id_custom)
        update_project.set("name", name)
        update_project.set("note", desc)
        update_project.set("planned_start_date", start)
        update_project.set("planned_end_date", end)
        update_project.saveIt()
        # go_to = "%s/t/IPM/copyds" % (ctxPath)
    
# DELETE PROJECT (will delete all scope and spec. under it)
if d_action == "delete_project":
    # project_id = request.get("project_id")
    spec_all = Prom_specification.where("project_id = ?", project_id)
    scop_all = Prom_scope.where("project_id = ?", project_id)
    project_all = Prom_project.findFirst("id = ?",project_id)
    junction_all = Prom_junction_project_team.where("project_id = ?", project_id)
    
    if spec_all is not None:
        for spec in spec_all:
            spec_data = Prom_specification.findFirst("project_id = ?", spec.get("project_id"))
            spec_data.delete()
    
    if scop_all is not None:
        for scope in scop_all:
            scope_data = Prom_scope.findFirst("project_id = ?", scope.get("project_id"))
            scope_data.delete()
    
    if junction_all is not None:
        for j in junction_all:
            junc_data = Prom_junction_project_team.findFirst("project_id = ?", j.get("project_id"))
            junc_data.delete()
            
    if project_all is not None:
        project_all.delete()
        go_to = "%s/t/IPM/copyds" % (ctxPath)

# END : MODAL UPDATE PROJECT

# START : MODAL UPDATE SCOPE

# GET data for SCOPE when any SCOPE in OVERALL PROJECT VIEW TREE is clicked
if d_action == "get_scope":
    data = request.get("id_scope")
    for key in data:
        scope = Prom_scope.findFirst("id_scope_custom = ?", key)
        scope_id = scope.get("id")
        name = scope.get("name")
        note = scope.get("note")
        start = scope.get("planned_start_date")
        end = scope.get("planned_end_date")
    output["scope_id"] = scope_id
    output["name"] = name
    output["note"] = note
    output["start"] = start
    output["end"] = end
    
# UPDATE SCOPE    
if d_action == "update_scope":
    # id_custom = request.get("id_scope_custom")
    # name = request.get("scope_name")
    # note = request.get("scope_desc")
    # start = request.get("scope_start")
    # end = request.get("scope_end")
    
    id_custom = request.get("data_form[id_scope_custom]")
    # check if scope name is used
    scope_name = str(scopeName).lower()
    allScope = Prom_scope.where("project_id = ? and id_scope_custom != ?", project_id, id_custom)
    scopeExist = 0
    scopeNameList = []
    for scope in allScope:
        scopeNameList.append(str(scope.get("name")).lower())
    
    if (scope_name in scopeNameList):
        scopeExist = 1
        output["scopeExist"] = 1
        
    if (scopeExist == 0):
        name = request.get("data_form[name]")
        note = request.get("data_form[desc]")
        start = request.get("data_form[start]")
        end = request.get("data_form[end]")
        
        for i in id_custom:
            update_scope = Prom_scope.findFirst('id_scope_custom = ?',i)
            update_scope.set("name",name[0])
            update_scope.set("note",note[0])
            update_scope.set("planned_start_date",start[0])
            update_scope.set("planned_end_date", end[0])
            update_scope.saveIt()
        
    # go_to = "%s/t/IPM/dsNew" % (ctxPath)
    
    # for i in id_custom:
    #     update_scope = Prom_scope.findFirst('id_scope_custom = ?',i)
    #     update_scope.set("name",name[0])
    #     update_scope.set("note",note[0])
    #     update_scope.set("planned_start_date",start[0])
    #     update_scope.set("planned_end_date", end[0])
    #     update_scope.saveIt()
    # go_to = "%s/t/IPM/copyds" % (ctxPath)

# DELETE SCOPE (will delete all spec. under it)
if d_action == "delete_scope":
    form_data = json.loads(data_form)
    
    # scope_id = request.get("id_scope")
    scope_id = form_data["scopeId"]
    id_scope_custom = form_data["scopeIdCustom"]
    
    # delete spec then scope
    spec_all = Prom_specification.where("scope_id = ?", scope_id)
    scope_all = Prom_scope.findFirst("id_scope_custom =?",id_scope_custom)
    
    if spec_all is not None:
        for spec in spec_all:
            spec_data = Prom_specification.findFirst("scope_id = ?", spec.get("scope_id"))
            spec_data.delete()
    if scope_all is not None:
        scope_all.delete()
    # go_to = "%s/t/IPM/copyds" % (ctxPath)

# END : MODAL UPDATE SCOPE

# START : MODAL UPDATE SPEC.

# GET data for SPEC. when any SPEC. in OVERALL PROJECT VIEW TREE is clicked
if d_action == "get_spec":
    data = request.get("id_spec")
    
    scope_id = 0
    unit_id = 0
    
    for i in data:
        spec = Prom_specification.findFirst("id_spec_custom = ?", i)
        spec_id = spec.get("id")
        name = spec.get("name")
        scope_id = spec.get("scope_id")
        scop = Prom_scope.findFirst("id = ?", scope_id)
        desc = spec.get("description")
        unit_id = spec.get("unit_id")
        dur = Prom_ref_duration.findFirst("id = ?", unit_id)
        assign = spec.get("assigned_id")
        emp = Employee.findFirst("id = ?", assign)
        project_id = spec.get("project_id")
        id_custom = spec.get("id_spec_custom")
        prom_scope = Prom_scope.where("project_id = ?", spec.get("project_id"))
        # all_employee = Base.findAll("Select * from employee")
        teamMember = Base.findAll("""
        SELECT e.full_name, e.id
        FROM employee e
        JOIN prom_project_team t ON e.id = t.emp_id
        JOIN prom_junction_project_team j ON j.project_team_id = t.id
        WHERE j.project_id = %s
        """ % project_id)
        duration_all = Base.findAll("select * from prom_ref_duration")
        tag_all = Prom_ref_tag.findAll()
        tag_select = Base.findAll("SELECT t.id, t.name FROM prom_ref_tag t JOIN prom_j_spec_tag j ON t.id = j.tag_id WHERE j.spec_id = %s" % spec.get("id"))
    
    output["spec_id"] = spec_id
    # output["employee_all"] = all_employee
    output["teamMember"] = teamMember
    output["duration_all"] = duration_all
    output["scope_all"] = prom_scope    
    output["name"] = name
    output["scope_name"] = scop
    output["desc"] = desc
    output["duration"] = dur
    output["assign_person"] = emp
    output["tagSelect"] = tag_select
    output["tag_all"] = tag_all
    
    tag_id = []
    for i in tag_select:
        tag_id.append(i.get("id"))
    output["tag_id_select"] = tag_id
    
# UPDATE SPEC.    
if d_action == "spec_update":
    form_data = json.loads(data_form)
    
    # check if spec. name is used
    spec_name = str(form_data["name"]).lower()
    allSpec = Prom_specification.where("project_id = ? and id != ?", project_id, form_data["specId"])
    specExist = 0
    specNameList = []
    for spec in allSpec:
        specNameList.append(str(spec.get("name")).lower())
    
    if (spec_name in specNameList):
        specExist = 1
        output["specExist"] = 1
        
    if (specExist == 0):
        name = form_data["name"]
        id_spec = form_data["specId"]
        id_scope = form_data["scope"]
        desc = form_data["desc"]
        person = form_data["assignedPerson"]
        duration = form_data["duration"]
        
        update_spec = Prom_specification.findFirst("id = ?" , id_spec)
        update_spec.set("name", name)
        update_spec.set("scope_id", id_scope)
        update_spec.set("description", desc)
        update_spec.set("assigned_id", person)
        update_spec.set("unit_id", duration)
        update_spec.saveIt()
        
        if form_data["tag"] is None:
            print "not tag"
        elif form_data["tag"] != None:
            print "has tag"
        
         # Spec. HAS NO TAG
        if form_data["tag"] is None:
            existingTag = Prom_j_spec_tag.where("spec_id = ?", id_spec)
            for a in existingTag:
                a.delete()
        
        # Spec. HAS TAG
        elif form_data["tag"] != None:
            # save tag
            existingTag = Prom_j_spec_tag.where("spec_id = ?", id_spec)
            newTagIdArr = []
            existingTagIdArr = []
            for a in form_data["tag"]:
                newTagIdArr.append(int(a))
            for b in existingTag:
                existingTagIdArr.append(int(b.get("tag_id")))
            for newTag in newTagIdArr:
                inDB = False
                for existingTag in existingTagIdArr:
                    if newTag == existingTag:
                        existingTagIdArr.remove(existingTag)
                        inDB = True
                        break
                if inDB == False:
                    jt = Prom_j_spec_tag()
                    jt.set("spec_id", id_spec)
                    jt.set("tag_id", newTag)
                    jt.saveIt()
            
            # delete tag from DB
            for a in existingTagIdArr:
                delTag = Prom_j_spec_tag.findFirst("spec_id = ? and tag_id = ?", id_spec, a)
                delTag.delete()

    # go_to = "%s/t/IPM/copyds" % (ctxPath)

# DELETE SPEC.
if d_action == "delete_spec":
    form_data = json.loads(data_form)
    
    # id_spec = request.get("id_spec")
    id_spec = form_data["specId"]
    del_spec = Prom_specification.findFirst("id = ?", id_spec)
    del_spec.delete()
    del_tag = Prom_j_spec_tag.where("spec_id = ?", id_spec)
    
    for tag in del_tag:
        tag_del = Prom_j_spec_tag.findFirst("tag_id = ?", tag.get("tag_id"))
        tag_del.delete()
    
    # go_to = "%s/t/IPM/copyds" % (ctxPath)

# END : MODAL UPDATE SPEC.

# END: CODE AQIL



