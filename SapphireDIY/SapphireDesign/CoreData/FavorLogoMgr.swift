//
//  FavorLogoMgr.swift
//  SapphireDesign
//
//  Created by gxwang on 15/9/19.
//  Copyright © 2015年 sapphire. All rights reserved.
//

import Foundation
import CoreData

class FavorLogoMgr:CoreDataBase {
    
    
    override func getEntityName() -> String {
        return "FavorLogo"
    }
    
    
    override func addCoreData(data: AnyObject) -> Bool {
        
        var favorLogo = FavorLogo(entity: getEntityDescription()!, insertIntoManagedObjectContext: GlobalVar.managerContext)
        
        favorLogo.convert()
        
        try! GlobalVar.managerContext.save()
        
        return true
    }
    
    
}
