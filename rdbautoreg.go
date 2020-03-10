package main

import (
	"fmt"
	//"github.com/go-redis/redis/v7"
	"github.com/go-redis/redis"
	//	"github.com/gomodule/redigo/redis"
	//	"gopkg.in/mgo.v2/bson"
	"net"
	"os/exec"
	//	"reflect"
	"bytes"
	"database/sql"
	_ "github.com/go-sql-driver/mysql"
	"strconv"
	"strings"
)

var (
	regUserName = "xxxx"
	regPassword = "xxx"
	regIp       = "xxx"
	regDbName   = "db_asset"
	regPort     = "3388"
)

var DB *sql.DB

func checkErr(err error) {

	if err != nil {
		fmt.Println(err)
		panic(err)

	}

}

func NetContainIP(netIP string, IP string) bool {
	//生产16位子网掩码。
	mask := net.IPv4Mask(byte(255), byte(255), byte(255), byte(0))
	//生成网段地址
	netMask := &net.IPNet{net.ParseIP(netIP), mask}
	//判断ip是否在网段中
	return netMask.Contains(net.ParseIP(IP))

}

func execShell(s string) (string, error) {
	cmd := exec.Command("/bin/bash", "-c", s)
	var out bytes.Buffer
	cmd.Stdout = &out
	err := cmd.Run()
	checkErr(err)
	return out.String(), err

}

func localIp() string {
	var ipAddr []string
	//获取所有的网卡。
	netInterfaces, err := net.Interfaces()
	if err != nil {
		fmt.Println("net.Interfaces failed, err", err.Error())
	}
	for i := 0; i < len(netInterfaces); i++ {
		// 排除没有启动的网卡，和以dock开头的网卡（docker启动的网卡）。
		if (netInterfaces[i].Flags&net.FlagUp) != 0 && !strings.Contains(netInterfaces[i].Name, "dock") {
			// 获取网卡地址。
			addrs, _ := netInterfaces[i].Addrs()
			for _, address := range addrs {
				// 排除本机回环地址 和子网掩码为32位的vip
				if ipnet, ok := address.(*net.IPNet); ok && !ipnet.IP.IsLoopback() && !strings.EqualFold(ipnet.Mask.String(), "ffffffff") {
					// 过滤不能转换位ipv4 和192.168.0.0/24 网段的地址。
					//if ipnet.IP.To4() != nil && !NetContainIP("192.168.0.0", ipnet.IP.String()) {
					if ipnet.IP.To4() != nil && (strings.Contains(ipnet.IP.String(), "192.168") || strings.Contains(ipnet.IP.String(), "10.100")) && !NetContainIP("192.168.0.0", ipnet.IP.String()) {
						//if ipnet.IP.To4() != nil {
						ipAddr = append(ipAddr, ipnet.IP.String())
					}
				}
			}

		}
	}
	return strings.Join(ipAddr, ",")
}

func insertDB(hostIp string, hostPort string, mIp string, mPort string, flag string) {
	//生成数据库连接地址
	regPath := strings.Join([]string{regUserName, ":", regPassword, "@tcp(", regIp, ":", regPort, ")/", regDbName, "?charset=utf8"}, "")
	//连接数据库
	regDB, _ := sql.Open("mysql", regPath)
	//判断数据库是否连接成功，如果失败打印日志到中断，并退出
	if err := regDB.Ping(); err != nil {
		fmt.Printf("open %s %s database fail\n", regIp, regPort)
		return
	}

	//prepare insert 语句
	stmt, err := regDB.Prepare(`replace into rdb_asset (ip, port, mip, mport, flag) values (?, ?, ?, ?, ?)`)
	checkErr(err)

	_, err = stmt.Exec(hostIp, hostPort, mIp, mPort, flag)
	checkErr(err)
	fmt.Printf("replace into rdb_asset (ip, port, mip, mport, flag) values (%s, %s, %s, %s, %s) \n", hostIp, hostPort, mIp, mPort, flag)
}

func getRedisHost(port string) (redisHostArr [][]string) {
        defer func() { // 必须要先声明defer，否则不能捕获到panic异常
                if err := recover(); err != nil {
                        fmt.Println(err)  // 这里的err其实就是panic传入的内容
                        fmt.Println(port) // 这里的err其实就是panic传入的内容
                        //return returnNil

                }
        }()
	IP := localIp()
	client := redis.NewClient(&redis.Options{
		//Addr: "10.100.90.162:8401",
		//Addr: "10.100.90.161:8401",
		Addr: "127.0.0.1:" + port,
		//Addr:     "localhost:8401",
		Password: "", // no password set
		DB:       0,  // use default DB
	})

	_, err := client.Ping().Result()
	checkErr(err)

	//fmt.Println(pong, err)
	//fmt.Println(IP)
	res, err := client.Do("role").Result()
	if res.([]interface{})[0] == "master" {

		//fmt.Println(len(res.([]interface{})))
		if len(res.([]interface{})[2].([]interface{})) != 0 {
			redisHostArr = append(redisHostArr, []string{IP, port, "", "", "0"})
			redisHostArr = append(redisHostArr, []string{res.([]interface{})[2].([]interface{})[0].([]interface{})[0].(string), res.([]interface{})[2].([]interface{})[0].([]interface{})[1].(string), IP, port, "1"})
		} else {

			redisHostArr = append(redisHostArr, []string{IP, port, "", "", "2"})
		}

	} else if res.([]interface{})[0] == "slave" {
		//	fmt.Println(res.([]interface{})[0])
		redisHostArr = append(redisHostArr, []string{IP, port, res.([]interface{})[1].(string), strconv.FormatInt(int64(res.([]interface{})[2].(int64)), 10), "1"})

	}
	//fmt.Println(redisHostArr)
	return redisHostArr
	// Output: key value
	// key2 does not exist
}

func main() {
	//redisPorts, _ := execShell("ps ax |grep -w  codis-server  |egrep -v 'sentinel|grep' |awk -F ':' '{print $NF}'|sort|uniq")
	redisPorts, _ := execShell("ps ax |grep -w  redis-server  |egrep -v 'sentinel|grep' |awk -F ':' '{print $NF}'|sort|uniq|awk '{print $1}'|grep '^[[:digit:]]*$'")
	for _, port := range strings.Fields(redisPorts) {
		fmt.Println(port)

		for _, regDB := range getRedisHost(port) {
			//fmt.Println(regDB)
			insertDB(regDB[0], regDB[1], regDB[2], regDB[3], regDB[4])
		}

	}
}
