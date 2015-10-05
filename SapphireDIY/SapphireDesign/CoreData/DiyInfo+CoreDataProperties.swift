//
//  DiyInfo+CoreDataProperties.swift
//  SapphireDesign
//
//  Created by gxwang on 15/9/19.
//  Copyright © 2015年 sapphire. All rights reserved.
//
//  Choose "Create NSManagedObject Subclass…" from the Core Data editor menu
//  to delete and recreate this implementation file for your updated model.
//

import Foundation
import CoreData

extension DiyInfo {

    @NSManaged var did: String?
    @NSManaged var all: String?
    @NSManaged var logo1: String?
    @NSManaged var logo2: String?
    @NSManaged var text1: String?
    @NSManaged var maker: String?
    @NSManaged var date: NSDate?
    @NSManaged var imageuse: String?

}
