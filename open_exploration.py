#!/usr/bin/env python
# coding: utf-8

# In[15]:


# import the required packages
from ema_workbench import (RealParameter,
                           BooleanParameter,
                           ScalarOutcome,
                           ArrayOutcome,
                           Policy,
                           MultiprocessingEvaluator,
                           save_results,
                           ema_logging)
from linnyr_connector import LinnyRModel_Botlek
import numpy as np

# for EMA Workbench
if __name__ == '__main__':

    # enable info logging
    ema_logging.log_to_stderr(ema_logging.INFO)

    # define a list with the models for the different perspectives and weeks
    model_list = []
    for perspective in ['collective', 'airliquide', 'nouryon', 'huntsman']:
        for week in range(1,11):
            model = LinnyRModel_Botlek(name = f'{perspective}week{week}', 
                                       wd = './models', 
                                       model_file = f'botlek_model_{perspective}_week_{week}.lnr')
            model_list.append(model)
                        
    # for every model in the model list
    for model in model_list:

        # define the uncertain factors
        model.uncertainties = [RealParameter(name = 'Scaling factor day-ahead electricity price (-)',
                                             variable_name = 'E day-ahead:Price',
                                             lower_bound = 0.7, 
                                             upper_bound = 1.3),
                               RealParameter(name = 'Gas price in 2030 (euro/Nm3)',
                                             variable_name = 'natural gas market:Price',
                                             lower_bound = 0.16, 
                                             upper_bound = 0.32),
                               RealParameter(name = 'CO2 emission price in 2030 (euro/ton)',
                                             variable_name = 'CO2 EUROPEAN EMISSION ALLOWANCES:Price',
                                             lower_bound = 21.0, 
                                             upper_bound = 150.0),
                               RealParameter(name = 'Hydrogen price in 2030 (euro/Nm3)',
                                             variable_name = 'H2 markt:Price',
                                             lower_bound = 0.12, 
                                             upper_bound = 0.30),
                               RealParameter(name = 'Cyclical frequency of NaOH 50% price (cycle/year)',
                                             variable_name = 'NaOH 50%:Price',
                                             lower_bound = 0.1, 
                                             upper_bound = 0.3),
                               RealParameter(name = 'Scaling factor upward balancing electricity price (-)',
                                             variable_name = 'Unbal opregelen:Price',
                                             lower_bound = 0.7, 
                                             upper_bound = 1.3),
                               RealParameter(name = 'Scaling factor downward balancing electricity price (-)',
                                             variable_name = 'Unbal afregelen:Price',
                                             lower_bound = 0.7, 
                                             upper_bound = 1.3),
                               RealParameter(name = 'Scaling factor electricity supply imbalance market (-)',
                                             variable_name = 'Unbal afregelen:LB',
                                             lower_bound = 0.7, 
                                             upper_bound = 1.3),
                               RealParameter(name = 'Scaling factor electricity demand imbalance market (-)',
                                             variable_name = 'Unbal opregelen:UB',
                                             lower_bound = 0.7, 
                                             upper_bound = 1.3),
                               RealParameter(name = 'E-boiler CAPEX (euro/MW)',
                                             variable_name = 'Capex E-boiler:Price',
                                             lower_bound = 1.4*10**6, 
                                             upper_bound = 2.0*10**6),
                               RealParameter(name = 'E-boiler OPEX (euro/MW/year)',
                                             variable_name = 'OPEX E-BOILER:Price',
                                             lower_bound = 2.8*10**3, 
                                             upper_bound = 4.0*10**3),
                               RealParameter(name = 'Steam Pipe CAPEX (euro)',
                                             variable_name = 'CAPEX Steam Pipe:Price',
                                             lower_bound = 6.0*10**6, 
                                             upper_bound = 12.0*10**6)]

        # define the levers (Power-to-X alternatives)
        model.levers = [BooleanParameter(name = 'E-boiler',
                                         variable_name = 'e_boiler'),
                        BooleanParameter(name = 'Steam Pipe',
                                         variable_name = 'steam_pipe'),
                        BooleanParameter(name = 'Chlorine Storage',
                                         variable_name = 'chlorine_storage')]

        # define the outcomes
        model.outcomes = [ScalarOutcome(name = 'Total cash flow of the cluster (euro/week)',
                                       variable_name = 'CF total',
                                       function = np.sum),
                          ScalarOutcome(name = 'Total cash flow of Air Liquide (euro/week)',
                                       variable_name = 'CF Air Liquide',
                                       function = np.sum),
                          ScalarOutcome(name = 'Total cash flow of Huntsman (euro/week)',
                                       variable_name = 'CF Huntsman',
                                       function = np.sum),
                          ScalarOutcome(name = 'Total cash flow of Nouryon (euro/week)',
                                       variable_name = 'CF Nouryon',
                                       function = np.sum),
                          ScalarOutcome(name = 'Total CO2 emissions (ton/week)',
                                       variable_name = 'CO2 emission',
                                       function = np.sum),
                          ScalarOutcome(name = 'Total green steam use by Air Liquide and Huntsman (ton/week)',
                                       variable_name= 'Use SP-A',
                                       function = np.sum),
                          ScalarOutcome(name = 'Total green steam use by Nouryon (ton/week)',
                                       variable_name = 'Use SP-B',
                                       function = np.sum),
                          ArrayOutcome(name = 'Chlorine storage stock at Nouryon (ton)',
                                       variable_name = 'Chlorine storage'),
                          ArrayOutcome(name = 'Run-time (s)',
                                       variable_name = 'Run-time')]
    
    # define the full factorial set of policies with names
    policies = [Policy('None of the options', **{'Steam Pipe':False, 'E-boiler':False, 'Chlorine Storage':False}),
                Policy('Only Steam Pipe', **{'Steam Pipe':True, 'E-boiler':False, 'Chlorine Storage':False}),
                Policy('Only E-boiler', **{'Steam Pipe':False, 'E-boiler':True, 'Chlorine Storage':False}),
                Policy('Only Chlorine storage', **{'Steam Pipe':False, 'E-boiler':False, 'Chlorine Storage':True}),
                Policy('Steam Pipe & E-boiler', **{'Steam Pipe':True, 'E-boiler':True, 'Chlorine Storage':False}),
                Policy('Steam Pipe & Chlorine storage', **{'Steam Pipe':True, 'E-boiler':False, 'Chlorine Storage':True}),
                Policy('E-boiler & Chlorine storage', **{'Steam Pipe':False, 'E-boiler':True, 'Chlorine Storage':True}),
                Policy('All options', **{'Steam Pipe':True, 'E-boiler':True, 'Chlorine Storage':True})]
              
    # define the number of scenarios to be sampled
    scenarios = 100

    # run the models
    with MultiprocessingEvaluator(model_list, n_processes = 56) as evaluator:
         results = evaluator.perform_experiments(policies = policies, scenarios = scenarios)
    
    # save the results
    save_results(results, f'./results/results_open_exploration_{scenarios}_scenarios_improved_model.tar.gz')

