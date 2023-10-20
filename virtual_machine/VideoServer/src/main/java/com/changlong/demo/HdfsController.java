package com.changlong.demo;

import javax.servlet.http.HttpServletRequest;
import org.apache.commons.io.IOUtils;
import org.springframework.http.HttpStatus;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FileStatus;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.io.InputStream;


@Controller
public class HdfsController {

    @GetMapping("/")
    public String index() {
        return "index";
    }

    @GetMapping("/listFiles")
    @ResponseBody
    public List<String> listHdfsFiles(@RequestParam(required = false) String search) {
        List<String> fileList = new ArrayList<>();

        // HDFS connection configuration
        Configuration conf = new Configuration();
        conf.set("fs.defaultFS", "hdfs://172.16.1.166:9000");
        System.setProperty("HADOOP_USER_NAME", "jichanglong");

        try {
            // Get HDFS file list
            FileSystem fs = FileSystem.get(conf);
            FileStatus[] status = fs.listStatus(new Path("/test"));

            // Extract file names and add them to the list
            for (FileStatus fileStatus : status) {
                String fileName = fileStatus.getPath().getName();
                if (search == null || fileName.contains(search)) {
                    fileList.add(fileName);
                }
            }

            fs.close();
        } catch (IOException e) {
            e.printStackTrace();
        }

        return fileList;
    }

    @GetMapping("/playVideo")
    @ResponseBody
    public ResponseEntity<byte[]> playVideo(@RequestParam String fileName) {
        // HDFS connection configuration
        Configuration conf = new Configuration();
        conf.set("fs.defaultFS", "hdfs://172.16.1.166:9000");
        System.setProperty("HADOOP_USER_NAME", "jichanglong");

        try {
            // Get the input stream of the video file
            FileSystem fs = FileSystem.get(conf);
            InputStream videoStream = fs.open(new Path("/test/" + fileName));

            // Read video file data and return the response
            byte[] videoData = IOUtils.toByteArray(videoStream);

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_OCTET_STREAM);
            headers.setContentDispositionFormData("attachment", fileName);

            return new ResponseEntity<>(videoData, headers, HttpStatus.OK);
        } catch (IOException e) {
            e.printStackTrace();
            return new ResponseEntity<>(HttpStatus.NOT_FOUND);
        }
    }

    @GetMapping("/getVisitorIP")
    @ResponseBody
    public Map<String, String> getVisitorIP(HttpServletRequest request) {
        Map<String, String> response = new HashMap<>();
        String visitorIP = request.getRemoteAddr();
        response.put("ip", visitorIP);
        return response;
    }
}