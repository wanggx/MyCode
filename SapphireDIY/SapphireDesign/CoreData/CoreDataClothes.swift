//
//  CoreDataClothes.swift
//  SapphireReleaseAutoLayOut
//
//  Created by gxwang on 15/8/8.
//  Copyright (c) 2015年 sapphire. All rights reserved.
//

import Foundation
import CoreData

class CoreDataClothes : CoreDataBase {
    
    func getClothesInfo(cid:String)->MarketItemInfo? {
        
        var predict = "cid contains '\(cid)'"
        var item = RecommandData().getCoreData(NSPredicate(format: predict, argumentArray: nil))
        
        if item != nil {
            return processCoreDataItem(item!) as? MarketItemInfo
        }
        
        item = MarketMgr(_type: nil).getCoreData(NSPredicate(format: predict, argumentArray: nil))
        if item != nil {
            return processCoreDataItem(item!) as? MarketItemInfo
        }

        return nil
    }
    
}