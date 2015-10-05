//
//  DetailInfoViewController.swift
//  SapphireDesign
//
//  Created by gxwang on 15/9/16.
//  Copyright (c) 2015年 sapphire. All rights reserved.
//

import Foundation
import UIKit

class DetailInfoViewController : UIViewController {
    
    @IBOutlet weak var tableView: UITableView!
    override func viewDidLoad() {
        super.viewDidLoad()
        self.title = "详情"
        //self.automaticallyAdjustsScrollViewInsets = false
        self.tableView.backgroundColor = UIColor.redColor()
    }
    
    override func viewWillLayoutSubviews() {
        //self.tableView.contentInset = UIEdgeInsets(top: 0, left: 0, bottom: 0, right: 0)
        //self.tableView.contentOffset = CGPoint(x: 0,y: 0)
        print("frame is \(self.tableView.frame)")
        print("contentInset is \(self.tableView.contentInset)")
        print("contentOffset is \(self.tableView.contentOffset)")
    }
    
    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
    }
    
}
