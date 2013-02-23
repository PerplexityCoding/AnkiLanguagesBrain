package fr.nfan.controller;

import java.io.IOException;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.servlet.ModelAndView;



@Controller
public class HomeController {

	@RequestMapping(value="/")
	public ModelAndView test() throws IOException{
		return new ModelAndView("home");
	}
}
