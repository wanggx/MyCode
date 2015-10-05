//
//  BottomTabBarControllers.swift
//  SapphireDesign
//
//  Created by 冯 波 on 15/8/22.
//  Copyright (c) 2015年 sapphire. All rights reserved.
//

import Foundation
import UIKit

var rootBarController:BottomTabBarControllers!

class BottomTabBarControllers:UITabBarController
{
    override func viewDidLoad()
    {
        super.viewDidLoad()
        
        initBottomControllerView()
    }
    
    func initBottomControllerView()
    {
        //设置页面
        let wallMarketView = MarketViewController()
        wallMarketView.title = "商城"
        wallMarketView.tabBarItem.image = UIImage(named:"market_Icon.png")
        
        let wallDesignView = DesignViewController()
        wallDesignView.title = "绘衣"
        wallDesignView.tabBarItem.image = UIImage(named: "design_Icon.png")
        
        let wallUserInfo = UserInfoViewController()
        wallUserInfo.title   = "我"
        wallUserInfo.tabBarItem.image = UIImage(named: "user_Icon.png")
        
        
        //添加四个控制器
        let ButtonMarket   = UINavigationController(rootViewController:wallMarketView )
        let ButtonDesign   = UINavigationController(rootViewController:wallDesignView)
        let ButtonUser     = UINavigationController(rootViewController:wallUserInfo)
        
        self.tabBar.barTintColor = UIColor(red: 0.2, green: 0.4, blue: 0.5, alpha: 0.3)
        self.tabBar.tintColor = UIColor.whiteColor()
        
        self.viewControllers = [
            
            ButtonMarket,ButtonDesign,ButtonUser
        ]
        
    }
    
    override func didReceiveMemoryWarning()
    {
        super.didReceiveMemoryWarning()
    }
    
    
}

