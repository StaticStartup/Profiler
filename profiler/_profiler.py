# Coding: utf-8

"""Profiling Module
Monitors the CPU and Memory usage of an application
"""

# Standard Library
import os
import time
import sys

# Third Party Library
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import multiprocessing as mp
import psutil


class Profiler:
    """
    Class used to profile CPU and Memory usage.
    """

    __start_time = None
    __q = None
    __prc_profiler = None

    @classmethod
    def __monitor(cls, q, prc_application_pid):
        """Monitors CPU and Memory.

        Parameters
        ----------
        q: Object
            Object of Queue Class

        prc_application_pid: Object
            Object of Process class
        """
        try:
            status = 0
            prc_profiler_pid = psutil.Process()

            int_cpu_count = cls.server_profile('cpu')
            str_cpu_max = str(int_cpu_count) + "00"

            lst_cpu = []
            lst_mem = []
            q_limit = False

            while psutil.pid_exists(prc_application_pid.pid):
                flt_total_cpu_usage = 0.0
                flt_total_mem_usage = 0.0
                prc_children = prc_application_pid.children(recursive=True)

                flt_total_child_cpu_usage = 0

                prc_application_pid.cpu_percent()
                for prc_child in prc_children:
                    prc_child.cpu_percent()

                time.sleep(5)

                for prc_child in prc_children:
                    if psutil.pid_exists(prc_child.pid):
                        flt_total_child_cpu_usage = flt_total_child_cpu_usage + prc_child.cpu_percent()
                        flt_total_mem_usage = flt_total_mem_usage + prc_child.memory_percent()
                flt_total_cpu_usage = prc_application_pid.cpu_percent() + flt_total_child_cpu_usage
                flt_total_mem_usage = prc_application_pid.memory_percent() + flt_total_mem_usage
                lst_cpu.append((flt_total_cpu_usage/float(str_cpu_max))*100)
                lst_mem.append(flt_total_mem_usage)
                if q_limit == True:
                    q.get()
                    q.get()

                q.put(status)
                q.put(lst_cpu)
                q.put(lst_mem)

                q_limit = True
        except Exception as error:
            status = 1
            q.put(status)
            q.put(error)

    @classmethod
    def server_profile(cls, option=None):
        """Retrieve CPU and Memory information.

        Parameters
        ----------
        option: str
            Default is None. Returns number of cpu cores, total memory, and available memory
            Optional parameter, available options: 'cpu' or 'memory'
        """
        cpu_count = psutil.cpu_count()
        total_mem = psutil.virtual_memory()[0] >> 30
        avail_mem = psutil.virtual_memory()[1] >> 30
        used_mem = psutil.virtual_memory()[3] >> 30
        if(option == None):
            return cpu_count, total_mem, avail_mem, used_mem
        elif(option == 'cpu'):
            return cpu_count
        elif(option == 'memory'):
            return total_mem, avail_mem, used_mem
        else:
            raise ValueError(
                "Invalid parameter, available options: cpu, memory")

    @classmethod
    def start_profiling(cls):
        """
        Begins profiling.
        """
        try:
            cls.__start_time = time.time()
            prc_application_pid = psutil.Process()
            cls.__q = mp.Queue()
            cls.__prc_profiler = mp.Process(target=cls.__monitor, args=(cls.__q, prc_application_pid))
            cls.__prc_profiler.start()
        except Exception as error:
            print("Start profiling got error: ", error)
            if(cls.__prc_profiler.is_alive()):
                cls.__prc_profiler.terminate()

    @classmethod
    def end_profiling(cls):
        """
        Ends Profiling and generates two graphs.
        """
        try:
            status = cls.__q.get()
            if status == 0:
                elapsed_time = time.time() - cls.__start_time
                lst_cpu = cls.__q.get()
                lst_mem = cls.__q.get()

                # Plot CPU
                cpu = [np.round(i, 2) for i in lst_cpu]
                avg_cpu = np.round(sum(lst_cpu)/len(lst_cpu), 2)
                cpu = [0.0] + cpu

                time_cpu = list(np.round(np.linspace(0, elapsed_time, len(cpu)), 2))
                plt.figure(figsize=(15,10))
                plt.plot(time_cpu, cpu)
                y_pos = np.arange(0, 105, step=5)
                y_list = list(np.arange(0, 105, step=5))
                plt.yticks(y_pos, y_list)
                plt.xlabel('Time(s)')
                plt.ylabel('CPU Usage(%)')
                plt.title('CPU Profiling')
                str_text = "Number of CPU Cores: " + str(cls.server_profile('cpu')) + "\n"
                str_text = str_text + "Max CPU Usage: " + str(np.round(max(lst_cpu), 2)) + " %\n"
                str_text = str_text + "Average CPU Usage: " + str(avg_cpu) + " %\n"
                plt.figtext(0.7, 0.7, str_text)
                plt.savefig('CPU_profiling.png')

                # Plot MEM
                mem = [np.round(i, 2) for i in lst_mem]
                avg_mem = np.round(sum(lst_mem)/len(lst_mem), 2)
                mem = [0.0] + mem
                time_mem = list(np.round(np.linspace(0, elapsed_time, len(mem)), 2))

                plt.figure(figsize=(15, 10))
                plt.plot(time_mem, mem)
                y_pos = np.arange(0, 105, step=5)
                y_list = list(np.arange(0, 105, step=5))
                plt.yticks(y_pos, y_list)
                plt.xlabel('Time(s)')
                plt.ylabel('MEM Usage(%)')
                plt.title('Memory Profiling')
                str_text = "Total Memory: " + str(cls.server_profile('memory')[0]) + " GB\n"
#                 str_text = str_text + "Used Memory: " + str(cls.server_profile('memory')[2]) + " GB\n"
#                 str_text = str_text + "Available Memory: " + str(cls.server_profile('memory')[1]) + " GB\n"
                str_text = str_text + "Max MEM usage: " + str(np.round(max(lst_mem), 2)) + " %\n"
                plt.figtext(0.7, 0.7, str_text)
                plt.savefig('MEM_profiling.png')

                if(cls.__prc_profiler.is_alive()):
                    cls.__prc_profiler.terminate()
            else:
                error = cls.__q.get()
                print("Profiler got error: ", error)
                if(cls.__prc_profiler.is_alive()):
                    cls.__prc_profiler.terminate()
        except Exception as error:
            print("End profiler got error: ", error)
            if(cls.__prc_profiler.is_alive()):
                cls.__prc_profiler.terminate()
