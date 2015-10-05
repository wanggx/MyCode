//
//  GlobalVar.swift
//  SapphireDesign
//
//  Created by gxwang on 15/9/8.
//  Copyright (c) 2015年 sapphire. All rights reserved.
//

import Foundation
import CoreData


class GlobalVar {
    static var UserInfo:UserModel = UserModel()
    
    
    static var managerContext:NSManagedObjectContext {
        return (UIApplication.sharedApplication().delegate as! AppDelegate).managedObjectContext as NSManagedObjectContext!
    }
}
