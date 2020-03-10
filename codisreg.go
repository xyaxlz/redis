package main

/**
客户端doc地址：github.com/samuel/go-zookeeper/zk
**/
import (
	"database/sql"
	"encoding/json"
	"fmt"
	_ "github.com/go-sql-driver/mysql"
	zk "github.com/samuel/go-zookeeper/zk"
	"strings"
	"time"
)

var (
	regUserName = "dbreg"
	regPassword = "xx"
	regIp       = "xxxx"
	regDbName   = "db_asset"
	regPort     = "3388"
)

type Kong struct {
}

type Server struct {
	Server        string
	Datacenter    string
	Action        Kong
	Replica_group bool
}

type Servers struct {
	Id          int
	Servers     []Server
	Promoting   Kong
	Out_of_sync bool
}

type ZkIdcAddr struct {
	ZkAddr []string
	Idc    string
}

var DB *sql.DB

/**
 * 获取一个zk连接
 * @return {[type]}
 */
func getConnect(zkList []string) (conn *zk.Conn) {
	conn, _, err := zk.Connect(zkList, 10*time.Second)
	if err != nil {
		fmt.Println(err)
	}
	return
}

func checkErr(err error) {

	if err != nil {
		fmt.Println(err)
		panic(err)

	}

}

//把获取的从库ip数组，和数据库名数组，插入到远程元数据数据库
func insertDB(hostIp string, port string, masterIp string, flag string, cacheName string, IDC string) {
	//生成数据库连接地址
	regPath := strings.Join([]string{regUserName, ":", regPassword, "@tcp(", regIp, ":", regPort, ")/", regDbName, "?charset=utf8"}, "")
	//fmt.Println(regPath)
	//连接数据库
	regDB, _ := sql.Open("mysql", regPath)
	//判断数据库是否连接成功，如果失败打印日志到中断，并退出
	if err := regDB.Ping(); err != nil {
		fmt.Printf("open %s %s database fail\n", regIp, regPort)
		return
	}

	//prepare insert 语句
	//stmt, err := regDB.Prepare(`replace into codis_asset (ip,port,mip,flag,cachename, idc) values (?, ?, ?, ?, ?, ?)`)
	stmt, err := regDB.Prepare(`insert  into codis_asset (ip,port,mip,flag,cachename,idc) values (?, ?, ?, ?, ?, ?)  ON DUPLICATE KEY UPDATE mip=values(mip),flag=values(flag),cachename=values(cachename) , idc=values(idc)`)
	checkErr(err)

	//循环从库ip数组远程注册到元数据库 flag为0
	//远程注册从库ip和端口到元数据库
	_, err1 := stmt.Exec(hostIp, port, masterIp, flag, cacheName, IDC)
	checkErr(err1)
	//fmt.Printf("replace into codis_asset (ip,port,mip,flag,cachename,idc) values (%s, %s, %s, %s, %s, %s) \n", hostIp, port, masterIp, flag, cacheName, IDC)
	fmt.Printf("insert  into codis_asset (ip,port,mip,flag,cachename,idc) values (%s, %s, %s, %s, %s, %s)  ON DUPLICATE KEY UPDATE mip=values(mip),flag=values(flag),cachename=values(cachename) , idc=values(idc) \n", hostIp, port, masterIp, flag, cacheName, IDC)

}

/**
 * 获取所有节点
 */
func getCodiesHosts(zkAddr []string) [][]string {
	zkList := zkAddr
	//zkList := []string{"10.100.90.163:4181"}
	conn := getConnect(zkList)

	defer conn.Close()

	children, _, err := conn.Children("/codis3")
	if err != nil {
		fmt.Println(err)
	}
	//fmt.Printf("%v \n", children)
	var m Servers
	var codisArr [][]string

	for _, ch := range children {
		//fmt.Printf("%d, %s\n", idx, ch)

		exists, _, err1 := conn.Exists("/codis3/" + ch + "/topom")
		checkErr(err1)
		if !exists {
			continue
		}

		children1, _, _ := conn.Children("/codis3/" + ch + "/group")
		//fmt.Printf("%v \n", children1)
		for _, ch1 := range children1 {

			//fmt.Printf(" %s\n", ch1)
			msg1, _, _ := conn.Get("/codis3/" + ch + "/group/" + ch1)
			//fmt.Printf(" %s\n", msg1)
			err1 := json.Unmarshal([]byte(msg1), &m)
			if err1 != nil {
				fmt.Println(err1)
			}

			if len(m.Servers) == 1 {
				codisArr = append(codisArr, []string{strings.Split(m.Servers[0].Server, ":")[0], strings.Split(m.Servers[0].Server, ":")[1], "", "2", ch})

			} else if len(m.Servers) == 2 {
				codisArr = append(codisArr, []string{strings.Split(m.Servers[0].Server, ":")[0], strings.Split(m.Servers[0].Server, ":")[1], "", "0", ch})
				codisArr = append(codisArr, []string{strings.Split(m.Servers[1].Server, ":")[0], strings.Split(m.Servers[1].Server, ":")[1], strings.Split(m.Servers[0].Server, ":")[0], "1", ch})

			}

		}
	}
	return codisArr

}

func getHostsInsert(zkAddr []string, IDC string) {
	hostsArr := getCodiesHosts(zkAddr)
	for _, hostArr := range hostsArr {
		insertDB(hostArr[0], hostArr[1], hostArr[2], hostArr[3], hostArr[4], IDC)
	}

}

func appendZkIdcAddr(zkIdcAddrArr []ZkIdcAddr, idc string, zkAddr []string) []ZkIdcAddr {

	var zkIdcAddr ZkIdcAddr
	zkIdcAddr.Idc = idc
	zkIdcAddr.ZkAddr = zkAddr
	zkIdcAddrArr = append(zkIdcAddrArr, zkIdcAddr)
	return zkIdcAddrArr

}

func main() {

	var zkIdcAddrArr []ZkIdcAddr

	//zkIdcAddrArr = appendZkIdcAddr(zkIdcAddrArr,"m5nodrc",[]string{})

	zkIdcAddrArr = appendZkIdcAddr(zkIdcAddrArr, "m5drc", []string{"10.100.21.122:5181", "10.100.21.123:5181", "10.100.21.124:5181", "10.100.21.125:5181", "10.100.21.126:5181"})
	zkIdcAddrArr = appendZkIdcAddr(zkIdcAddrArr, "yzdrc", []string{"10.100.96.69:5181", "10.100.96.70:5181", "10.100.96.71:5181", "10.100.96.245:5181", "10.100.96.246:5181"})

	zkIdcAddrArr = appendZkIdcAddr(zkIdcAddrArr, "m5nodrc", []string{"10.100.21.122:6181", "10.100.21.123:6181", "10.100.21.124:6181", "10.100.21.125:6181", "10.100.21.126:6181"})
	zkIdcAddrArr = appendZkIdcAddr(zkIdcAddrArr, "yznodrc", []string{"10.100.96.69:6181", "10.100.96.70:6181", "10.100.96.71:6181", "10.100.96.245:6181", "10.100.96.246:6181"})

	zkIdcAddrArr = appendZkIdcAddr(zkIdcAddrArr, "m5single", []string{"10.100.21.122:7181", "10.100.21.123:7181", "10.100.21.124:7181", "10.100.21.125:7181", "10.100.21.126:7181"})
	//zkIdcAddrArr = appendZkIdcAddr(zkIdcAddrArr,"yzsingle",[]string{})

	zkIdcAddrArr = appendZkIdcAddr(zkIdcAddrArr, "m5old1", []string{"10.100.20.16:2181", "10.100.20.17:2181", "10.100.20.18:2181"})
	zkIdcAddrArr = appendZkIdcAddr(zkIdcAddrArr, "m5old2", []string{"10.100.20.16:2182", "10.100.20.17:2182", "10.100.20.18:2182"})
	//zkIdcAddrArr = appendZkIdcAddr(zkIdcAddrArr,"m5old3",[]string{})

	fmt.Println(zkIdcAddrArr)

	for _, zkIdcAddr := range zkIdcAddrArr {
		//	fmt.Println(zkIdcAddr.Idc)
		//	fmt.Println(zkIdcAddr.ZkAddr)
		getHostsInsert(zkIdcAddr.ZkAddr, zkIdcAddr.Idc)

	}

}
