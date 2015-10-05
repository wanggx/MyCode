//
//  ShopCarViewController.swift
//  SapphireDesign
//
//  Created by gxwang on 15/9/15.
//  Copyright (c) 2015年 sapphire. All rights reserved.
//

import Foundation
import UIKit

class ShopCarViewController : UIViewController {
    
    @IBOutlet weak var tableView: ShopCarTableView!
    override func viewDidLoad() {
        super.viewDidLoad()
        self.title = "购物车"
        self.view.backgroundColor = UIColor.redColor()
        initTableView()
    }
    
    
    private func initTableView() {
        tableView.initTableView()
    }
    
    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
    }
    
    
    @IBAction func payBtnClicked(sender: AnyObject) {
        log.info("payBtnClicked")
        let viewController = self.storyboard?.instantiateViewControllerWithIdentifier("OrderViewControllerID") as UIViewController!
        self.navigationController?.pushViewController(viewController, animated: true)
        
    }
}
