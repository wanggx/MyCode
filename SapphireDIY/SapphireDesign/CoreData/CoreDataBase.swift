//
//  CoreDataBase.swift
//  SapphireReleaseAutoLayOut
//
//  Created by gxwang on 15/7/21.
//  Copyright (c) 2015年 sapphire. All rights reserved.
//

import Foundation
import CoreData
import SwiftyJSON
import Alamofire

typealias CALLBACK = (Int)->()

class CoreDataBase : NSObject {
    
    func reFreshDataFromNet(block:CALLBACK?)->Request? {
        log.info("reFreshDataFromNet(block:AnyObject?)")
        return getNetRequest()?.responseJSON(){
            (_,_,data) in
            if data.isFailure == true {
                block?(ERROR_CODE_REFRESH_ERROR)
                return
            }
            var json:JSON = JSON(data.value!)
            self.processJSONData(json)
            block?(ERROR_CODE_NO_ERROR)
        }
    }
    
    func getNetRequest()->Request? {
        log.info("getNetRequest()->Request?")
        return nil
    }
    
    func addJSONData(json:JSON)->Bool {
        log.info("addJSONData(json:JSON)->Bool")
        return true
    }
    
    func processJSONData(json:JSON)->Bool {
        for i in 0..<json.count {
            self.addJSONData(json[i])
            log.info("\(json[i])")
        }
        return true
    }
    
    func getFetchRequest()->NSFetchRequest? {
        log.info("NSFetchRequest is default")
        var fetchRequest = NSFetchRequest(entityName: getEntityName())
        fetchRequest.sortDescriptors = []
        return fetchRequest
    }
    
    func getEntityDescription()->NSEntityDescription? {
        log.info("getEntityDescription()->NSEntityDescription?")
        return NSEntityDescription.entityForName(getEntityName(), inManagedObjectContext: GlobalVar.managerContext)
    }
    
    func getEntityName()->String {
        log.info("please implement this function")
        return "Entity"
    }
    
    func getFetchedResultController()->NSFetchedResultsController? {
        var fetchRequest = getFetchRequest()
        if fetchRequest == nil {
            return nil
        }
        var frc = NSFetchedResultsController(fetchRequest: fetchRequest!, managedObjectContext: GlobalVar.managerContext, sectionNameKeyPath: nil, cacheName: nil)
        return frc
    }
    
    func processCoreDataItem(item:AnyObject)->AnyObject? {
        log.info("CoreDataBase processCoreDataItem")
        return nil
    }
    
    func getCoreData(inout dataList:[AnyObject],condition:((AnyObject)->Bool)?) {
        dataList.removeAll(keepCapacity: true)
        log.info("getCoreData(inout dataList:[AnyObject])")
        var frc = getFetchedResultController()
        try! frc?.performFetch()
        log.info("count is \(frc?.sections?[0].numberOfObjects)")
        for (var i=0; i < frc?.sections?[0].numberOfObjects; ++i) {
            var index:NSIndexPath = NSIndexPath(forRow: i, inSection: 0)
            let item: AnyObject = frc!.objectAtIndexPath(index)
            var dataItem: AnyObject? = processCoreDataItem(item)
            if dataItem == nil || condition?(dataItem!) == false {
                continue
            }
            dataList.append(dataItem!)
        }
    }
    
    func addCoreData(data:AnyObject)->Bool {
        log.info("addCoreData(data:AnyObject)")
        return false
    }
    
    func getCoreData(predicate:NSPredicate)->NSManagedObject? {
        var fetchRequest = getFetchRequest()
        log.info(predicate.predicateFormat)
        fetchRequest?.predicate = predicate
        var fetchResult = try! GlobalVar.managerContext.executeFetchRequest(fetchRequest!)
        if fetchResult.count > 0 {
            return fetchResult[0] as? NSManagedObject
        }
        return nil
    }
    
    func deleteCoreData(predicate:NSPredicate)->Bool {
        log.info("deleteCoreData(data:NSPredicate)")
        var fetchRequest = getFetchRequest()
        fetchRequest?.predicate = predicate
        var fetchResult = try! GlobalVar.managerContext.executeFetchRequest(fetchRequest!)
        log.info("deleteCount is \(fetchResult.count)")
        if fetchResult.count == 0 {
            return false
        }
        for var i=0;i<fetchResult.count;++i {
            var object:NSManagedObject = fetchResult[i] as! NSManagedObject
            GlobalVar.managerContext.deleteObject(object)
        }
        try! GlobalVar.managerContext.save()
        return true
    }
    
    func clearCoreData() {
        log.info("clearCoreData()")
        var fetchResultControl = getFetchedResultController()
        try! fetchResultControl?.performFetch()
        
        for var i=0;i<fetchResultControl?.sections?[0].numberOfObjects;++i {
            var index:NSIndexPath = NSIndexPath(forRow: i, inSection: 0)
            var deleteItem = fetchResultControl?.objectAtIndexPath(index) as! NSManagedObject
            GlobalVar.managerContext.deleteObject(deleteItem)
        }
        try! GlobalVar.managerContext.save()
    }
    
    func IsExist(condition:[String:String])->Bool {
        var fetchRequest = getFetchRequest()
        var format = ""
        var i=0
        
        for con in condition {
            format += (con.0 + " contains '" + con.1 + "' ")
            if i++ != condition.count-1 {
                format += " and "
            }
        }
        log.info("format is \(format)")
        
        var predicate:NSPredicate = NSPredicate(format: format,argumentArray: nil)
        fetchRequest!.predicate = predicate
        var fetchResult = try! GlobalVar.managerContext.executeFetchRequest(fetchRequest!) as? [NSManagedObject]
        
        if fetchResult == nil || fetchResult?.count == 0 {
            log.info("not exist")
            return false
        }
        log.info("alread exist")
        return true
    }
    
    func checkCycle(predicate:NSPredicate,block:((AnyObject)->Bool)?) {
        var fetchRequest = getFetchRequest()
        fetchRequest?.predicate = predicate
        if fetchRequest == nil {
            return
        }
        var fetchResult = try! GlobalVar.managerContext.executeFetchRequest(fetchRequest!)
        
        for var i=0;i<fetchResult.count;++i {
            block?(fetchResult[i])
        }
        try! GlobalVar.managerContext.save()
    }
    
    deinit {
        log.info("CoreDataBase \(self.description)")
    }
}